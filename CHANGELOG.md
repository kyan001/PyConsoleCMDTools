# Change Log
## Updates
* 2025-01-17 v6.6.3:
    * Bug Fix: `is_cmd_exist()` now only checks the base command without the args.
* 2024-11-30 v6.6.2:
    * Improvement: `resolve_value()` now support UPPERCASE/lowercase/Titlecase on platform name.
* 2024-08-17 v6.6.1:
    * Feature: Add `resolve_value()` to get the value for current platform.
* 2024-07-10 v6.5.2:
    * Bug Fix: `is_cmd_exist()` now return False even the command is a path with `~`.
* 2024-07-10 v6.5.1:
    * Bug Fix: `move_file()` escape "\" in path automatically.
* 2024-07-01 v6.5.0:
    * Feature: Add support for 'pipx' as package manager.
* 2021-01-29 v3.0.0:
    * Deprecated `image_to_color()`, add `main_color()`.
        * use `main_color(..., is_url=True)` instead of `image_to_color(...)`
