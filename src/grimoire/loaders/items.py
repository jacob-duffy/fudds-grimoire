"""Load and save item catalog YAML files under .data/items/."""

from pathlib import Path

import yaml

from grimoire.models.item import TYPE_TO_FILE

# Default data directory, resolved relative to the process working directory.
DEFAULT_DATA_DIR = Path(".data") / "items"

# Schema comment written to the top of every catalog file.
_SCHEMA_COMMENT = "# yaml-language-server: $schema=../../.schemas/items.schema.json\n"


class ItemCatalogLoader:
    """Loads and saves item catalog YAML files.

    Each item type maps to a single YAML file (e.g. weapons.yml, armor.yml).
    Files are created on first save if they do not already exist.
    """

    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir: Path = data_dir if data_dir is not None else DEFAULT_DATA_DIR

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def file_for_type(self, item_type: str) -> Path:
        """Return the catalog Path for the given item type."""
        filename = TYPE_TO_FILE.get(item_type, "items.yml")
        return self.data_dir / filename

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, item_type: str) -> dict:
        """Load the catalog for *item_type*.

        Returns ``{"items": {}}`` when the file does not exist or is empty.
        """
        path = self.file_for_type(item_type)
        if not path.exists():
            return {"items": {}}
        with open(path, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        if not isinstance(content, dict) or "items" not in content:
            return {"items": {}}
        return content

    def save_item(self, item_type: str, item_id: str, item_data: dict) -> Path:
        """Append (or overwrite) *item_id* in the catalog for *item_type*.

        Creates the file and any intermediate directories if they do not exist.
        Returns the path of the written catalog file.
        """
        path = self.file_for_type(item_type)
        path.parent.mkdir(parents=True, exist_ok=True)

        catalog = self.load(item_type)
        catalog["items"][item_id] = item_data

        with open(path, "w", encoding="utf-8") as fh:
            fh.write(_SCHEMA_COMMENT)
            yaml.dump(
                catalog,
                fh,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        return path
