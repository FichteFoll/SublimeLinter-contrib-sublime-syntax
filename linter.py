#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by FichteFoll
# Copyright (c) 2016 FichteFoll
#
# License: MIT
#

"""This module exports the SublimeSyntax plugin class."""

import contextlib
import re
import os.path

import sublime
import sublime_api

from SublimeLinter.lint import Linter, persist


# For debug printing
p_name = "sublime-syntax"


class SublimeSyntax(Linter):

    """Provides an interface to sublime-syntax.

    This linter uses Sublime Text's internal sublime_api module
    to access the syntax test running code.

    Because that has rather harsh requirements,
    we rely on creating temporary files in the Packages folder
    in order to provide the full functionality.
    """

    # Must be active on all syntaxes,
    # so we can check view's eligibility in the `run` method.
    syntax = '*'
    cmd = None
    regex = (
        r'^[^:]+:(?P<line>\d+):((?P<col>\d+):)? '
        r'(?P<message>.+)'
    )
    word_re = r'.'  # only highlight a single character

    @classmethod
    def can_lint_view(cls, view, settings):
        """Check if file is 'lintable'."""
        # Check `super` first bc it has the cheap, fast checks, e.g.
        # if this linter has been disabled.
        if not super().can_lint_view(view, settings):
            return False

        filename = view.file_name() or ''
        basename = os.path.basename(filename)
        if not basename or not basename.startswith("syntax_test"):
            # This actually gets reported by the test runner,
            # so we only check for an additionally qualifying file
            # if the filename check fails.
            code = view.substr(sublime.Region(0, view.size()))
            first_line = code[:code.find("\n")]
            match = re.match(r'^(\S*) SYNTAX TEST "([^"]*)"', first_line)
            if not match:
                return False

        return True

    def run(self, cmd, code):
        """Perform linting."""

        # The syntax test runner only operates on resource files that the resource loader can load,
        # which must reside in a "Packages" folder
        # and has the restriction of only working on saved files.
        # Instead, we create a temporary file somewhere in the packages folder
        # and pass that.
        with _temporary_resource_file(code, prefix="syntax_test_") as resource_path:
            assertions, test_output_lines = sublime_api.run_syntax_test(resource_path)

        output = "\n".join(test_output_lines)

        if persist.debug_mode():
            basename = os.path.basename(self.filename)
            persist.printf('{}: "{}" assertions: {}'.format(p_name, basename, assertions))
            # SublimeLinter internally already prints the output we return
            # persist.printf('{}: "{}" output: \n  {}'.format(p_name, basename,
            #                                                 "\n  ".join(test_output_lines)))

        return output


##################################################
# Utility for temporary resource files

_temp_dir_name = ".temp-subsyn-lint"
_temp_path = None


def plugin_loaded():
    """Build and remove temporary path."""
    # Required for sublime.packages_path().
    # ST only "loads resources" from the Packages dir.
    global _temp_path
    packages_path = sublime.packages_path()
    _temp_path = os.path.join(packages_path, _temp_dir_name)

    _remove_temp_path()


def plugin_unloaded():
    """Remove temporary path."""
    # Don't block plugin unloading by not catching an exception
    try:
        _remove_temp_path()
    except Exception:
        import traceback
        traceback.print_exc()


def _remove_temp_path():
    """Try to clean our temp dir if it exists."""
    if os.path.exists(_temp_path):
        if os.path.isdir(_temp_path):
            def onerror(function, path, excinfo):
                persist.printf("{}: Unable to delete '{}' while cleaning up temporary directory"
                               .format(p_name, path))
                import traceback
                traceback.print_exc(*excinfo)
            import shutil
            shutil.rmtree(_temp_path, onerror=onerror)
        else:
            persist.printf("{}: For some reason, '{}' is a file. Removing..."
                           .format(p_name, _temp_path))
            os.remove(_temp_path)


@contextlib.contextmanager
def _temporary_resource_file(text, prefix='', suffix=''):
    """Create a temporary file in ST's "resource" folder, using tempfile.mkstemp.

    Yields the relative resource path as a context manager
    and removes it when the scope is exited.

    Files are stored in a Temp folder relative to the Data folder,
    which is removed afterwards if it does not contain any other files.
    """
    import tempfile

    # Ensure the folder exists
    if not os.path.exists(_temp_path):
        os.mkdir(_temp_path)

    try:
        fd, temp_file_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=_temp_path)
        if persist.debug_mode():
            persist.printf("{}: created temporary file at {}".format(p_name, temp_file_path))

        try:
            with open(fd, 'w', encoding='utf-8') as f:
                f.write(text)
            temp_file_resource_path = "/".join(["Packages", _temp_dir_name,
                                                os.path.basename(temp_file_path)])
            yield temp_file_resource_path
        finally:
            os.remove(temp_file_path)
    except FileNotFoundError:
        _remove_temp_path()
    finally:
        # And remove the folder, if it's empty.
        # Otherwise wait for a "restart".
        try:
            os.rmdir(_temp_path)
        except OSError as e:
            if persist.debug_mode():
                persist.printf("{}: unable to delete temporary folder; {}".format(p_name, e))
