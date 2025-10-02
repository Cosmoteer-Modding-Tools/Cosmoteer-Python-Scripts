# Active Context

## Current Focus
- Establish baseline understanding of Cosmoteer Image Destroyer and capture project knowledge in the Memory Bank.

## Recent Activity
- Reviewed `damage_painter.py`, README, and support scripts to document architecture, presets, and tooling.
- Bootstrapped Memory Bank core files to support future session resets.

## Decisions & Considerations
- Treat provided defaults (33/50/66) as canonical until new presets are requested.
- Maintain Windows batch tooling alongside Python entry point since packaging workflow relies on it.
- Preserve deterministic seeding scheme when extending the pipeline to ensure reproducibility.

## Next Steps (Potential)
- Audit asset folders for coverage (e.g., ensure `_33`/`_66` pairs exist) before adding new presets.
- Identify pain points in GUI UX (e.g., additional preview controls or warnings) once user feedback arrives.

## Insights
- Image pipeline is modular enough to accept new overlay layers with minimal coupling.
- Dynamic asset loading means documentation should clearly state naming patterns for contributors.
