SublimeLinter-contrib-sublime-syntax
================================

This linter plugin for [SublimeLinter][docs] provides an interface to Sublime Text's internal syntax testing engine. It will be used on files that define syntax tests for Sublime Text (i.e. files starting with `syntax_test_`).

![screenshot](https://cloud.githubusercontent.com/assets/931051/14467995/26f9885e-00de-11e6-8261-8a1cd91f1d0c.png)

*Notice*: This linter relies on undocumented and unpublic API of Sublime Text and may break on any new Sublime Text release.

**You must be using Sublime Text Build 3092 or higher in order to install and use this linter.**

## Installation

SublimeLinter must be installed in order to use this plugin. If SublimeLinter is not installed, please follow the instructions [here][installation].

### Plugin installation

Please use [Package Control][pc] to install the linter plugin. This will ensure that the plugin will be updated when new versions are available. If you want to install from source so you can modify the source code, you probably know what you are doing so we won’t cover that here.

To install via Package Control, do the following:

1. Within Sublime Text, bring up the [Command Palette][cmd] and type `install`. Among the commands you should see `Package Control: Install Package`. If that command is not highlighted, use the keyboard or mouse to select it. There will be a pause of a few seconds while Package Control fetches the list of available plugins.

1. When the plugin list appears, type `sublime-syntax`. Among the entries you should see `SublimeLinter-contrib-sublime-syntax`. If that entry is not highlighted, use the keyboard or mouse to select it.

## Settings

For general information on how SublimeLinter works with settings, please see [Settings][settings]. For information on generic linter settings, please see [Linter Settings][linter-settings].

[docs]: http://sublimelinter.readthedocs.org
[installation]: http://sublimelinter.readthedocs.org/en/latest/installation.html
[locating-executables]: http://sublimelinter.readthedocs.org/en/latest/usage.html#how-linter-executables-are-located
[pc]: https://packagecontrol.io/installation
[cmd]: http://docs.sublimetext.info/en/sublime-text-3/extensibility/command_palette.html
[settings]: http://sublimelinter.readthedocs.org/en/latest/settings.html
[linter-settings]: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html
[inline-settings]: http://sublimelinter.readthedocs.org/en/latest/settings.html#inline-settings
