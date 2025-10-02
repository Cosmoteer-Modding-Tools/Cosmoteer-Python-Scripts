# Project Brief

## Goal
Deliver a desktop tool that procedurally "damages" Cosmoteer sprite textures by combining stencil-driven hole cutting with scorch and shrapnel overlays, giving modders reusable destruction presets.

## Scope
- Ship a user-friendly PySide6 GUI (`damage_painter.py`) for loading a base image, configuring destruction presets (levels 33/50/66), previewing the result, and exporting PNGs.
- Support runtime discovery of asset packs (`assets/` stencils, covers, scorches, shrapnel) with sensible defaults and deterministic randomization via seeds.
- Provide packaging scripts (batch helpers, PyInstaller spec) so non-developers can run either from source or as a standalone executable.

## Constraints
- Preserve alpha transparency and avoid altering already-transparent pixels unless covered by assets.
- Limit dependencies to Pillow and PySide6 to keep distribution lightweight.
- Target Windows-first workflows, but keep code cross-platform where possible.

## Success Criteria
- Modders can drag a PNG into the app, tweak settings, and export damage variants with predictable naming (`<original>_<level>.png`).
- Asset folders remain hot-swappable without code changes.
- Project can be built into a single-file executable with provided scripts.
