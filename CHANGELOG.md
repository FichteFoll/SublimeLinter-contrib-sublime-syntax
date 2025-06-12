SublimeLinter-contrib-sublime-syntax Changelog
==============================================

v2.0.1 (2025-06-12)
-------------------

- Fixed a regression in the first line check, causing it not to function at all.


v2.0.0 (2025-06-12)
-------------------

- Update for new syntax test output of build 4181+. (#6, @camila314, @FichteFoll)
- Make the first line match more accurate when determining whether the linter should be active. (#7)
- Require the file name prefix to be `syntax_test_` with the trailing underline, just like the ST core.
- Mark plugin as compatible with the Python 3.8 plugin host.


v1.1.2 (2019-06-11)
-------------------

- Poll ST until the resource file can be found (and get rid of the workaround)


v1.1.1 (2019-03-01)
-------------------

- Include a workaround for when ST hasn't found our temporary test file yet (#4)
- Use SL4's new logging framework


v1.1.0 (2018-09-11)
-------------------

- Use a better method to decide whether a view shows a test file (#3)


v1.0.2 (2016-11-04)
-------------------

- Add fallbacks for when the path is a file


v1.0.1 (2016-05-01)
-------------------

- Fix linting of unicode files (#1)


v1.0.0 (2016-05-01)
-------------------

- initial release
