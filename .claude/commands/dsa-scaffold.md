# dsa-scaffold

Scaffold a new DSA data structure module and/or its tests.

## Usage

```
python scripts/dsa.py create-<type>          # module + tests
python scripts/dsa.py create-<type>-module   # module only
python scripts/dsa.py create-<type>-tests    # tests only
```

### Options

| Flag | Description |
|------|-------------|
| `--root <path>` | Project root (default: script's parent's parent) |
| `--src <path>` | Source package folder, relative to root (default: `dsa`) |
| `-u` | Create unit test folder with `__init__.py` and `test_<name>.py` |
| `-i` | Create integration test folder with `__init__.py` |
| `-p` | Create performance test folder with `__init__.py` |

When none of `-u`/`-i`/`-p` are given, all three folders are created (default).

## When to use

When the user invokes `/dsa-scaffold` followed by a command like
`create-deque`, `create-linked_list-module`, or `create-stack-tests`.

## Instructions

1. Run the scaffolding script with the user's arguments:

   ```bash
   python scripts/dsa.py $ARGUMENTS
   ```

   Always use the script — never create the scaffold files by hand.

2. After the script finishes, print the list of created/skipped files so
   the user can see what happened.