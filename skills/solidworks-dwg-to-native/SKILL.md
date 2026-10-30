---
name: solidworks-dwg-to-native
description: Use when converting DWG/DXF or engineering drawings into editable native SolidWorks SLDPRT models, especially when sketches must be fully constrained to the origin or imported solids lack editable feature history.
---

# DWG to editable native SolidWorks

Use native sketches, dimensions, relations and modeling features for an editable
SolidWorks request. A STEP import is exchange geometry, not the requested feature
history. This local extension coexists with the upstream `cad` skill without editing
its vendored files. For a generic Python-to-STEP or 2D-only request, use the appropriate
existing skill instead.

## Workflow

1. Read [environment setup](references/environment-setup.md) and inspect the current
   PC's installed tools. Skill installation does not install/license SolidWorks or
   AutoCAD and does not establish runtime readiness.
2. Use `$image-to-cad` for DWG/DXF vector extraction and its
   [evidence handoff](../image-to-cad/references/solidworks-handoff.md). Preserve source
   geometry, map orthographic views, record explicit versus inferred dimensions and
   settle the origin/datum before construction.
3. Read [native modeling and verification](references/solidworks-native.md). Build
   editable bosses, cuts, suitable Hole Wizard holes, fillets and drafts with actual
   origin constraints, rather than blanket Fix relations.
4. Read [API recovery notes](references/solidworks-api-notes.md) when automating.
   Treat version-specific observations as evidence to verify, not universal flags.
5. Exercise controlling dimensions, rebuild, restore, save/reopen by exact path and
   inspect the final native feature tree and geometry. Use `$cad` for optional STEP
   inspection/snapshots; do not substitute a STEP result for the native deliverable.

Deliver SLDPRT, an edit/parameter guide and checks actually run; include STEP when
requested or useful. State any unresolved/inferred internal geometry and tested
software version. Other design applications require their own native API/feature
implementation and validation; the SolidWorks COM recipes are not portable to them.
