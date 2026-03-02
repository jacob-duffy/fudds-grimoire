# Fudd's Grimoire

Fudd's Grimoire helps dungeon masters create, manage, and run configurable loot tables for tabletop RPGs.

The project uses user-defined YAML loot tables to represent sources of loot (vendors, chests, encounters, etc.), applies contextual rules (rarity, level, vendor type), and selects items randomly according to those rules.

## Goals

- Provide a simple, human-editable YAML format for loot tables.
- Let DMs express contextual conditions (vendor type, encounter level, rarity guarantees).
- Offer deterministic seeding for reproducible random loot when desired.
- Be easy to integrate into scripts or small apps used at the table.

## Key Concepts

- Loot Table: a named collection of entries with weights or conditions.
- Entry: an item or nested table reference with weight, tags, and optional conditions.
- Context: runtime information applied when selecting loot (e.g., `vendor: blacksmith`, `encounter_level: 3`).
- Rarity / Guarantees: rules to ensure a minimum rarity or to reroll until conditions are met.

## Example Use Cases

- Generating merchant inventory for different vendor types (blacksmith vs. apothecary).
- Filling chest contents with level-appropriate and rarity-filtered items.
- Random trinket tables for exploration rewards or quest rewards.

## Getting Started

1. Create a YAML loot table describing sources and entries.
2. Run the terminal application to browse and sample tables interactively.

This project is intended as a terminal application (Textual-based prototype). It provides a small interactive TUI to load YAML tables, set context (vendor, encounter level, etc.), and sample loot from tables. It is not built as a command-line batch sampler; instead it focuses on an interactive terminal experience.

## Running the terminal application (development)

Run the app from source using your Python environment:

```bash
python main.py
```

(If you want, I can add a `requirements.txt` or `pyproject.toml` entries for `textual` and other dependencies.)

## YAML Loot Table Example

```yaml
# tables.yml
tables:
  blacksmith_inventory:
    description: "Items typically sold by a blacksmith"
    entries:
      - item: "Iron Sword"
        weight: 10
        tags: [weapon, common]
      - item: "Steel Longsword"
        weight: 4
        tags: [weapon, uncommon]
      - item: "Reinforced Shield"
        weight: 3
        tags: [armor, uncommon]

  small_chest_lvl1:
    description: "Small chest for level 1 encounters"
    entries:
      - reference: blacksmith_inventory
        weight: 1
      - item: "Healing Herbs"
        weight: 6
        tags: [consumable, common]
      - item: "Silver Trinket"
        weight: 1
        tags: [trinket, uncommon]
```

Notes:

- `reference` can include other table names to nest tables.
- `weight` controls relative probability among siblings.
- `tags` and optional `conditions` can be used by the runtime to filter entries.

### Minimal YAML Schema (informal)

- root: `tables` (map)
- table:
  - `description`: string (optional)
  - `entries`: list of entry
- entry:
  - either `item: <string>` or `reference: <table-name>`
  - `weight`: number (defaults to 1)
  - `tags`: list of strings (optional)
  - `conditions`: map (optional) — runtime context keys that must match for the entry to be eligible

***
License and distribution

This project uses a non-commercial license (see `LICENSE`). The repository is intended for personal, educational, and non-commercial use only; commercial use is not permitted by anyone, including the project author.

***
