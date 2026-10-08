# Data policy

External inputs, processed copies, model weights and generated outputs are ignored by Git and excluded from imported histories. Do not force-add them.

## Prepare an assignment

Use Python 3.10+ and the original course environment. Run the assignment's `download_data.py` by path from any directory; it writes into that assignment.

```bash
python download_data.py --list
python download_data.py
python download_data.py --archive-root /path/to/github-organization/migration-archive
python download_data.py --archive-root /path/to/github-organization/migration-archive --include-artifacts
```

`--list` performs no downloads. The archive restores exact historical bytes; `--include-artifacts` additionally restores original figures, exports and model outputs. `MIGRATION_ARCHIVE` can supply the archive directory. Matching checksums are reused and failed downloads do not replace existing files. Manifest paths cannot escape the assignment directory.

Retain the local archive when deleting source repositories. Authenticated GitHub fallback requires `gh` and source access, and stops working after deletion. URLs without a checksum are not certified as reproducing historical bytes. HTML confirmation/authentication responses are rejected; Google Drive and other hosts may need additional access.

Library providers use existing `torchvision` or `ucimlrepo` dependencies without installing or upgrading them. UCI providers cache the fetched dataset object as pickle; notebooks retain their original preprocessing/fetch workflow. Use trusted local pickle files. The PDB provider delegates to the original validated structure downloader.

An assignment's `DATA.md` lists inputs and known gaps; `data_sources.json` records checksums, archive paths and source references. Missing inputs cause nonzero exit status. No replacement datasets are fabricated. Legacy analyses are not claimed to execute end to end; scientific review is a later stage.

Support checks from the collection root: `python -m unittest discover -s tests -v`.
