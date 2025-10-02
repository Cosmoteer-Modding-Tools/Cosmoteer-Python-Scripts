# Tech Context

## Languages & Frameworks
- Python 3.10+.
- PySide6 for GUI, QSettings persistence, and splash screens.
- Pillow for alpha-aware image manipulation.

## Tooling & Scripts
- `setup.bat` sets up a Windows venv, upgrades pip, installs requirements.
- `run.bat` activates the venv and launches `damage_painter.py`.
- `build_app.bat` and `CosmoteerImageDestroyer.spec` package the app via PyInstaller with bundled assets and icons.

## Assets & Data
- `assets/` holds runtime-discovered content: `hole_punch`, `hole_covers`, `scorches`, `shrapnel`.
- `default_images/` contains splash art used by the optional QSplashScreen.

## Dependency Notes
- Pillow>=10.0 and PySide6==6.9.1 are pinned in `requirements.txt`.
- Randomization uses Python's stdlib `random`; no external RNG dependencies.

## Platform Considerations
- Batch scripts assume Windows shells; PySide6 app remains cross-platform when run via `python damage_painter.py`.
- PyInstaller config targets a single-file GUI executable with icon metadata.
