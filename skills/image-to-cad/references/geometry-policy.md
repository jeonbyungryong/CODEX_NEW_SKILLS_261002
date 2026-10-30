# Geometry policy

## Source priority

1. DXF analytic/vector entities.
2. DWG converted to DXF by an installed converter.
3. Native vector paths extracted from PDF.
4. Calibrated raster contours.
5. Uncalibrated raster contours in pixels only.

## Closure

Ingestion accepts open and closed paths. Area, nesting, offsets, and die-cut output require a closed region. Keep two geometry layers: immutable source paths and a calculation copy. Snap endpoints only on the calculation copy and only when their distance is no greater than the configured tolerance. Record every automatic closure in `report.json`; normalized source output must retain the supplied coordinates.

Evaluate geometric closure independently from the CAD entity's closed flag. A spline or mixed line/arc chain is closed when its endpoints form an even-degree connected chain after tolerance snapping. Preserve open source entities even when their group forms a valid closed region.

Use full polygonization diagnostics. Classify a group as `closed`, `closed_after_snap`, `open_unresolved`, or `invalid`, and report unmatched endpoint count plus dangle, cut, and invalid-ring lengths. A model may remain semantically valid while `open_unresolved`; only its area-dependent operations are unavailable. Never bridge a larger gap merely because the missing segment appears visually obvious.

## Multiple shapes and intersections

Preserve all supported source entities and full drawing bounds. Build visual groups from endpoint connectivity and geometric intersections. Overlapping closed paths belong to one visual group but remain independent production contours. Intersecting mixed chains remain one visual group; polygonized internal faces are calculation regions, not separate user models.

Validate the exact output file by checking entity counts by type, visual group count, production-region count, closed state, and extents before relying on area values.

## Dimensions and PDF annotations

Inventory native CAD `DIMENSION` entities but do not convert them into production paths. For vector PDFs, exclude text blocks and filled arrowheads, polygonize unfilled linework, retain source paths that materially contribute to closed-region boundaries, and remove a shorter path when it is almost entirely coincident with a longer retained boundary. Keep counts of source drawings, text blocks, filled annotation paths, and excluded annotation paths in the report.

Apply the PDF page rotation matrix to extracted coordinates. Keep PDF geometry in points unless a trustworthy scale is supplied; dimension text alone is not sufficient to infer a global scale without associating it with measured extension points.

PDF semantic separation is structure-first. Treat optional-content-group names as supporting evidence, never as fixed category IDs. Infer template content from page borders, title-block grids, margins, and repeated sheet-text structure; infer model content from contour continuity and view clusters; infer dimensions from center marks, extension lines, arrowheads, and glyph runs; infer special specifications from filled feature symbols and multiline glyph runs connected to diagonal leaders. Preserve unresolved records as `unknown` with confidence and evidence.

Hard-coded source indices, page coordinates, layer names, and filenames are prohibited. Validate generalization by renaming groups, permuting input record order, changing page dimensions, and holding out at least one drawing family from rule development.

## Drawing templates and title blocks

Classify template content from entities actively placed in modelspace. Ignore unused block definitions: CAD exports often carry title-block and dimension-symbol definitions even when the model-only drawing does not insert them.

Mark a layer as a template layer when it contains supported geometry and either its name contains a strong template hint (`SLD`, `TITLE`, `BORDER`, `FRAME`, `FORMAT`, `NOTE`, `TEMPLATE`, or `SHEET`) or active text/title-block entities dominate its geometric entity count. Do not use `DIMENSION` entities alone to mark a whole layer as template; dimensions frequently share layer `0` with valid model geometry.

Preserve geometry-dominated mixed layers. Exclude only supported geometry on classified template layers, while inventorying all annotation entities. Report template layer names, excluded template geometry count, and annotation entity count. A template-only drawing should yield no production contour rather than small false regions from title-block marks.

Recursively decompose active block inserts. If the expanded insert contains text or annotation entities, classify its supported linework as template geometry and render it separately. If it contains only supported geometry, retain it as model geometry. Report template/model insert counts and template path count.

Some sheet symbols are raw layer-0 LINE entities rather than blocks. Only when a template has already been detected, estimate a robust model core from path-center quantiles and move short isolated LINE marks outside that core to the template set. Report `isolated_template_mark_count`; never use this spatial rule alone to infer a template.

## Curves

Preserve analytic CIRCLE and ARC entities in normalized DXF where practical. Flatten bulges, ellipses, and splines for polygon calculations using maximum sagitta tolerance. Report tolerance as approximation uncertainty.

For raster drawings, classify stroke semantics before contour extraction. Use Hough/LSD-style straight-line evidence together with a dimension network: extension lines, a perpendicular dimension line, arrow or label context, and overlap with the candidate silhouette. Never remove a true straight product edge based on straightness alone.

When a confirmed dimension stroke occludes a curved boundary, preserve the source mask, remove the stroke only from a calculation mask, estimate endpoints and inward direction from neighboring contour geometry, and create a bounded smooth repair. Report the source segment, repair endpoints, maximum displacement, confidence, and rejection reason. Rejected or ambiguous repairs remain `unknown` and must not be used for production area.

## Units

Use `$INSUNITS` when present. Unitless CAD remains unitless unless the user supplies a known measurement. Raster input requires `--mm-per-pixel` for physical dimensions.

## Confidence

- High: vector source, valid closed calculation contour, known units, no forced gap closure.
- Medium: vector source with tolerance closure, or calibrated raster with clean contours.
- Low: missing scale, ambiguous multiple contours, large open gaps, or noisy raster.

Low-confidence results require user review before production use.
