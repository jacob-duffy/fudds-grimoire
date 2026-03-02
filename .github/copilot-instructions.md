# Remember

- This project uses `uv` to manage its python environment. Make sure to reference the `uv` documentation for setup and usage: https://pypi.org/project/uv/
- All packages not required for a production deployment should be installed in the `dev` environment.
- The main file to run the application is `main.py`.
- The application uses `textual` for its TUI framework. Refer to the `textual` documentation for any UI-related customizations: https://textual.textualize.io/
- Use `uv pytest` to run the test suite.
- Tests are located in the `tests/` directory.
- Test coverage must be at least 90% with no failures for a new feature or bug fix to be merged.
- YAML loot tables are defined in `.yml` files, typically located in the `.data/` directory.
