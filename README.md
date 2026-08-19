# Delete When Unzip — Linux Edition

Stream-extract large ZIP/RAR archives while deleting already-processed parts as you go, so you don't need double the disk space to unpack a huge archive. A 100 GB archive extracts with roughly 100 GB + a bit of headroom, instead of 200 GB.

Linux fork of [auto-Dog/delete_when_unzip](https://github.com/auto-Dog/delete_when_unzip).

> ⚠️ The source archive is destroyed during extraction. If extraction is interrupted, the archive is left damaged. Back up anything you can't afford to lose first.

## Install (Arch-based distros)

```bash
git clone https://github.com/sven-7777/delete_when_unzip-for-linux.git
cd delete_when_unzip-for-linux
makepkg -si
```

## Uninstall

```bash
sudo pacman -Rns delete-when-unzip-git
```

## Install (other distros)

```bash
git clone https://github.com/sven-7777/delete_when_unzip-for-linux.git
cd delete_when_unzip-for-linux
sudo ./install.sh
```

Supports Debian/Ubuntu (`apt`) and Fedora (`dnf`). Other distros: the script installs the Python packages via pip and prints what to install manually via your package manager (`tkinter`, `libarchive`, `unrar`). Installs system-wide — no virtual environment.

**Uninstall:**
```bash
sudo ./uninstall.sh
```

## Usage

Launch the GUI (`delete-when-unzip`, or `python3 app.py`), pick your archive, choose a mode, set a chunk size, and run.

| Mode | Use for |
|---|---|
| Single file, zip/tar.gz | A single `.zip` or `.tar.gz` |
| Single file, RAR | A single `.rar` |
| Single file, alternate | Backup engine for single RAR |
| Multi-volume, zip | Segmented ZIPs (`.zip.001`, `.z01`) — point at the first volume |
| Multi-volume, rar | Segmented RARs (`.part1.rar`, `.r01`) — point at the first volume |
| Multi-volume, alternate | Fallback for other segmented formats |

Output is written to a folder next to the archive. The archive's internal folder structure is preserved.

### Command line

```bash
python3 delete_when_unzip.py <archive> [chunk_size_bytes] [password]
python3 delete_when_unzip_rar.py <archive> [chunk_size_bytes] [password]
python3 delete_when_unzip_multi.py <first_volume> [chunk_size_bytes] [password]
python3 delete_when_unzip_cli.py <first_volume> [chunk_size_bytes] [password]
python3 delete_when_unzip_rar_multi.py <first_volume> [chunk_size_bytes] [password]
```
Default chunk size is 512 MB if omitted.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `unrar not found` | Install your distro's `unrar` package |
| `ModuleNotFoundError` on launch | Activate your venv: `source venv/bin/activate` |
| `Rar!` in the error message | Wrong mode selected — switch to a RAR mode |
| `str object cannot be interpreted as an integer` | Wrong mode for this file type — switch single ↔ multi-volume |

## License

MIT, inherited from [auto-Dog/delete_when_unzip](https://github.com/auto-Dog/delete_when_unzip).
