# Working on REMADE

The maintained application is in `remade/`; `REMADEDEMO.py` is its launcher. Keep camera/GUI code in `vision`, math in `geometry`, device transport and actions in `robot`/`vacuum`, and scheduling in `monitor`.

Run the offline checks before publishing changes:

```bash
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
python tools/build_code_index.py
python tools/check_repository.py
```

Do not import or execute archived `test*.py` files for verification. Some connect to real devices at module scope. New regression tests belong in `tests/` and substitute only device/model boundaries.

Keep `legacy/` and `references/` as traceable snapshots. For intentional changes to historical files, document the reason and update the corresponding migration manifest record; never silently regenerate hashes to conceal an unexpected change. Keep source attributions intact.

Model, calibration, class mapping, grasp height and motion changes require separate lab validation. Record which hardware, controller firmware, checkpoint and settings were actually used. Offline CI does not establish physical readiness.
