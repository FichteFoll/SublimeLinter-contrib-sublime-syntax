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
import logging
import re
import os

import sublime
import sublime_api

from SublimeLinter.lint import Linter

logger = logging.getLogger("SublimeLinter.plugin.sublime-syntax")


class SublimeSyntax(Linter):

    """Provides an interface to sublime-syntax.

    This linter uses Sublime Text's internal sublime_api module
    to access the syntax test running code.

    Because that has rather harsh requirements,
    we rely on creating temporary files in the Packages folder
    in order to provide the full functionality.
    """

    cmd = None  # We implement a custom `run` method
    regex = (
        r'^[^:]+:(?P<line>\d+):((?P<col>\d+):)? '
        r'(?P<message>.+)'
    )
    # An empty selector matches all views
    defaults = {
        'selector': ''
    }
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

        # Fast path
        if basename and basename.startswith("syntax_test"):
            return True

        # But, essentially all files can be syntax tests, if they contain
        # a magic first line
        first_line = view.substr(view.line(0))
        match = re.match(r'^(\S*) SYNTAX TEST "([^"]*)"', first_line)
        if match:
            return True

        return False

    def run(self, cmd, code):
        """Perform linting."""
        if not code:
            return

        # The syntax test runner only operates on resource files that the resource loader can load,
        # which must reside in a "Packages" folder
        # and has the restriction of only working on saved files.
        with _temporary_resource_file(code, prefix="syntax_test_") as resource_path:
            # Some change in ST caused the newly created file not to get picked up in time,
            # so we wait until the file can be loaded.
            import time
            start_time = time.time()
            while time.time() <= start_time + 1:
                try:
                    sublime.load_binary_resource(resource_path)
                except OSError:
                    logger.debug("ST couldn't find our temporary file; re-polling…")
                    time.sleep(0.1)
                else:
                    break
            else:
                logger.warning("Waiting for ST to find our temporary file '%r' timed out",
                               resource_path)

            assertions, test_output_lines = sublime_api.run_syntax_test(resource_path)

        logger.debug('assertions: {}'.format(assertions))
        output = "\n".join(test_output_lines)
        if "unable to read file" in output:
            logger.error(output)

        return output


##################################################
# Utility for temporary resource files

_temp_dir_name = ".temp-subsyn-lint"
_temp_path = None


def plugin_loaded():
    """Build and remove temporary path.

    Required for sublime.packages_path()
    because ST only "loads resources" from the Packages dir.
    """
    global _temp_path
    packages_path = sublime.packages_path()
    _temp_path = os.path.join(packages_path, _temp_dir_name)

    _remove_temp_path()


def plugin_unloaded():
    """Remove temporary path."""
    # Don't block plugin unloading by not catching an exception.
    # Has been fixed in 3189.
    try:
        _remove_temp_path()
    except Exception:
        import traceback
        traceback.print_exc()


def _remove_temp_path():
    """Try to clean our temp dir if it exists."""
    if os.path.exists(_temp_path):
        if os.path.isdir(_temp_path):
            def onerror(function, path, exc_info):
                logger.exception("Unable to delete '%s' while cleaning up temporary directory",
                                 path, exc_info=exc_info)
            import shutil
            shutil.rmtree(_temp_path, onerror=onerror)
        else:
            logger.warning("For some reason, '%s' is a file. Removing...", _temp_path)
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
        logger.debug("created temporary file at '%s'", temp_file_path)

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
            logger.debug("unable to delete temporary folder; %s", e)
