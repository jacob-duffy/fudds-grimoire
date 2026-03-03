"""Load and save loot table YAML files under .data/tables/."""

from pathlib import Path

import yaml

# Default data directory, resolved relative to the process working directory.
DEFAULT_TABLES_DIR = Path(".data") / "tables"

# Schema comment written to the top of every table file.
_TABLE_SCHEMA_COMMENT = (
    "# yaml-language-server: $schema=../../.schemas/loot-table.schema.json\n"
)


class LootTableLoader:
    """Reads and writes loot table YAML files.

    Responsibilities:
    - Enumerate available table files so the UI can populate a dropdown.
    - Load a specific table file.
    - Append an inline one-off ``item:`` entry to an existing table's entries.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir: Path = data_dir if data_dir is not None else DEFAULT_TABLES_DIR

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_tables(self) -> list[tuple[str, Path]]:
        """Return ``(label, path)`` pairs for every ``.yml`` file in *data_dir*.

        The label is the table's ``id`` field when present, falling back to the
        filename stem.  Results are sorted alphabetically by label.  Returns an
        empty list when the directory does not exist.
        """
        if not self.data_dir.exists():
            return []

        results: list[tuple[str, Path]] = []
        for path in sorted(self.data_dir.glob("*.yml")):
            label = path.stem
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = yaml.safe_load(fh)
                if isinstance(data, dict) and isinstance(data.get("id"), str):
                    label = data["id"]
            except Exception:  # noqa: BLE001
                pass
            results.append((label, path))

        results.sort(key=lambda t: t[0])
        return results

    def load(self, path: Path) -> dict:
        """Load and return a loot table from *path*.

        Returns an empty ``{"id": "", "entries": []}`` skeleton when the file
        does not exist or cannot be parsed.
        """
        if not path.exists():
            return {"id": "", "entries": []}
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        except Exception:  # noqa: BLE001
            return {"id": "", "entries": []}
        if not isinstance(data, dict):
            return {"id": "", "entries": []}
        if "entries" not in data:
            data["entries"] = []
        return data

    def append_inline_item(
        self,
        path: Path,
        item_data: dict,
        weight: int = 1,
    ) -> None:
        """Append a new inline ``item:`` entry to an existing loot table.

        The entry is written as::

            - item:
                name: ...
              weight: <weight>

        Creates the file with a minimal valid skeleton if it does not exist yet.
        """
        table = self.load(path)

        entry: dict = {"item": item_data, "weight": weight}
        table["entries"].append(entry)

        # Ensure the file's parent directories exist.
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(_TABLE_SCHEMA_COMMENT)
            yaml.dump(
                table,
                fh,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
