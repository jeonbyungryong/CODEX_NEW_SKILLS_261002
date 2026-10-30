---
name: image-to-cad
description: Use when reconstructing measurable CAD contours from DWG, DXF, PNG, JPG, or scanned drawings; diagnosing wrong curve recognition, bulge/arc loss, open endpoints, scale uncertainty, or image-to-vector conversion.
---

# Image to CAD

## Core principle

Preserve native CAD vectors before considering pixels. Use OpenCV only for raster-only sources, and never claim physical dimensions without calibration.

## Workflow

1. Run the reconstruction script:

```powershell
uv run scripts/reconstruct_geometry.py --input <drawing> --output-dir <folder> --mode auto --tolerance-mm 0.05
```

2. Inspect all outputs:
   - `normalized.dxf`: for DWG/DXF, the unchanged source DXF (or ODA-converted DXF), retaining analytic entities, units, blocks and annotations. Select model contours using the report/previews; do not extrude this whole document. For PDF/raster, this is sampled polyline geometry with declared units or unitless coordinates.
   - `preview.png`: every source path, colored and numbered by visual shape group.
   - `model-preview.png`: production/model geometry without group labels.
   - `template-preview.png`: separately reconstructed drawing border, title block, and note geometry.
   - `dimension-preview.png`: dimension, extension-line, and center-mark candidates.
   - `special-preview.png`: leader-connected callouts, THRU/GDT candidates, and filled feature symbols.
   - `unknown-preview.png`: unresolved geometry that must not be silently treated as a model.
   - `report.json`: entity inventory, visual groups, production regions, source/calculation open paths, endpoint snaps, polygonization leftovers, units, dimensions, area, approximation error, warnings, confidence.
3. Show the preview to the user before modifying consuming software.
4. Treat open curves as valid input diagnostics. Require closure only for area, nesting, offsets, or die-cut regions.
5. Read [references/geometry-policy.md](references/geometry-policy.md) before changing tolerances, interpreting low-confidence results, or integrating with another importer.
6. When the requested output is an editable SolidWorks model, read
   [the native-model handoff](references/solidworks-handoff.md), then use the installed
   `$solidworks-dwg-to-native` [native workflow](../solidworks-dwg-to-native/references/solidworks-native.md).
   Extracted vectors are source evidence; importing them as a fixed sketch or a STEP
   body does not satisfy native feature editability or origin-based full constraints.

## Input routing

Resolve commands from this installed skill directory (or use absolute script paths).
For a new PC, read the native skill's [environment setup](../solidworks-dwg-to-native/references/environment-setup.md)
when SolidWorks conversion is requested. The synthetic validation below uses no
private drawings; passing it does not verify ODA or SolidWorks availability.

| Input | Route |
|---|---|
| DXF | Vector reconstruction; ignore unsupported DIMENSION entities while inventorying them |
| DWG | Installed ODA converter, then vector reconstruction |
| Vector PDF | PyMuPDF path reconstruction; remove text, filled arrowheads, dangling dimension branches, and coincident duplicate dimension strokes |
| Hybrid PDF | Inspect embedded-image coverage; reconstruct the embedded product drawing as raster geometry and combine it with retained PDF vectors |
| PNG/JPG/BMP/TIFF | OpenCV contour reconstruction |
| Raster without scale | Pixel geometry only; no millimetre claim |

For calibrated raster input, pass `--mm-per-pixel`. If scale is unavailable, keep `unit=pixel` and ask for one known dimension.

## Required behavior

- Preserve LINE, ARC, CIRCLE, ELLIPSE, SPLINE, POLYLINE, and LWPOLYLINE bulge geometry.
- Preserve every supported source entity; never select only the largest contour from a multi-shape drawing.
- For CAD dimensions, inventory `DIMENSION` entities but exclude them from production paths.
- Detect drawing-template layers from active modelspace, not unused block definitions or filenames. Exclude geometry on layers with template-name hints or a dominant population of text/title-block entities.
- Recursively expand active block inserts. Classify an insert containing text or annotation entities as template content; retain a purely geometric insert as model content.
- When an active sheet template is present, treat small isolated LINE marks outside the robust model core as template symbols. Do not apply this spatial rule to drawings without a detected template.
- Keep model geometry on a mixed layer when geometric entities outnumber template signals; a few dimensions or inserts must not cause the whole layer to be discarded.
- For vector PDFs, retain paths that form production-region boundaries and remove filled arrowheads, text, dangling branches, and shorter coincident duplicates.
- For CAD-derived PDFs, infer optional-content-group roles from page-relative geometry, border/title-grid structure, closed model contours, center marks, arrowheads, leader runs, and glyph clusters. Layer names are weak evidence only.
- Never encode sample layer names, source-object index ranges, absolute page coordinates, or a drawing filename as semantic classification rules.
- Keep uncertain PDF groups in `unknown` and report category evidence and confidence rather than forcing them into model geometry.
- Apply the PDF page rotation matrix before previewing geometry.
- Group paths for visual review using endpoint adjacency and geometric intersections while keeping production regions separately measurable.
- Flatten curves using maximum sagitta tolerance, not fixed visual guesses.
- Keep source geometry immutable. Perform endpoint repair only on a separate calculation copy.
- Auto-close only endpoint gaps within tolerance and report the applied gap, repair point, and affected shape group.
- Never silently bridge larger gaps.
- Use full polygonization diagnostics to report dangling lines, cut edges, and invalid rings. Do not discard an open model merely because it has no calculable area.
- Preserve holes by containment.
- Verify entity count, group count, complete drawing bounds, and closed flags before accepting a preview.
- Prefer vector-derived geometry over an OpenCV trace when both are available.
- For raster engineering drawings, detect labelled dimension-line networks before tracing the product silhouette. A long straight line alone is not sufficient evidence.
- Detect both horizontal dimension baselines and vertical extension lines. Remove connected dimension symbols that create narrow interior spikes, but preserve intentional edge hooks and straight product edges.
- For PDFs, inventory embedded images before accepting vector-only output. A large image containing the product view must not be silently ignored merely because the page also has vector paths.
- Move confirmed dimension strokes to a separate mask/layer, then reconstruct an occluded curved boundary from neighboring endpoints and inward curvature. Keep low-confidence repairs in `unknown`.
- Validate raster repairs against annotated curve and dimension masks when the user supplies them; annotations are regression truth, never runtime coordinates.
- For EPDM importers, reuse the vector path/flattening logic; do not rasterize CAD first.

## Common mistakes

- Reading `LWPOLYLINE.get_points("xy")` discards bulge arcs.
- Treating every open path as invalid loses useful CAD geometry.
- Writing snapped calculation coordinates back to normalized source output destroys evidence and can alter the supplied design.
- Treating every near endpoint as connected invents material.
- Converting pixels to millimetres without calibration creates false precision.
- Selecting the largest contour without reviewing holes or separate parts can choose the wrong model.
- Treating polygonized faces as user models can split one intersecting drawing into several false models.
- Expanding every block definition imports unused title blocks and note symbols. Inspect only active modelspace inserts when deciding whether a block participates in the drawing.
- Treating all layer `0` content as template or all nonzero layers as model is unsafe; classify from active entity composition.
- Rasterizing a vector PDF before inspecting its paths mixes dimensions and product geometry and loses curve precision.
- Mapping PDF layer `3` to dimensions or a fixed rectangle to `THRU` merely memorizes one export and will fail on a new template.
- Tracing the largest connected raster component before removing touching dimensions merges extension lines, leaders, and the product boundary.
- Removing a touching dimension line without reconstructing the hidden curve leaves a false straight edge or an open contour.

## Validation

Run:

```powershell
uv run scripts/validate_samples.py
```

Then test the real artifact and inspect its preview and JSON report. Do not rely on a passing synthetic test alone.

When matching dimensioned and undimensioned versions, compare retained path count, visual group count, production-region count, normalized area ratios, and the preview - not raw source drawing counts.

When template-only and model-only reference drawings are supplied, verify that the template produces zero production paths and that the model retains its complete geometric inventory. Report `template_layers`, `excluded_template_entity_count`, and `annotation_entity_count`.

For PDF semantic validation, rename every optional-content group and shuffle the input record list while retaining source record IDs. Categories must remain stable. Also test a different page size and template placement; inspect all five previews.

For raster semantic validation, include (1) a dimensioned curved product, (2) the same product with annotated model curves, (3) annotated dimension strokes, and (4) a true straight-edged product without dimensions. Require separate model/dimension masks and bounded curve-to-annotation distance.
