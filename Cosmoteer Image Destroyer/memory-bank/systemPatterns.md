# System Patterns

## Architecture Overview
- Single-file PySide6 application (`damage_painter.py`) with helper batch scripts and PyInstaller spec for packaging.
- GUI (`App` QMainWindow) owns UI widgets, user settings (QSettings), and orchestrates the image pipeline.
- Image processing pipeline is composed of pure Pillow helpers: stencil hole cutting (`apply_stencil_holes` + `soft_erase`), rim burning, and layered stamping (`stamp_layer`).
- Assets are discovered dynamically via filesystem scanning; grouped by suffix (_33, _66) to control preset levels.

## Key Flows
1. **Load Base** ? Pillow loads RGBA base image and stores in memory.
2. **Parameter Refresh** ? UI widgets push values into a `Params` dataclass and throttle render via QTimer.
3. **Pipeline Execution** ? `apply_pipeline` composes hole masks, applies scorches/shrapnel overlays, then reinserts covers; respects transparency masks.
4. **Preview & Save** ? Result converted to `QPixmap` for preview; save dialog proposes `<stem>_<level>.png` in last-used folder.

## Important Behaviors
- Deterministic randomness: seeds are XORed with constants per layer to keep independent noise patterns.
- 50% damage level blends results from both `_33` and `_66` stencil sets at half density.
- Stamps are restricted to non-transparent pixels post-holes to avoid floating scorch marks.

## Extension Points
- Additional overlays can plug into the pipeline after stamp generation.
- New preset defaults can be introduced by expanding `Params` and `_set_level` logic.
- Asset scanning is resilient to missing folders; gracefully skips absent stamp sets.
