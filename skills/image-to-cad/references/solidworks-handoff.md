# DWG/DXF evidence for an editable SolidWorks model

Read when vector reconstruction feeds a native SolidWorks SLDPRT request.
This skill owns source interpretation; the installed `$solidworks-dwg-to-native`
[native workflow](../../solidworks-dwg-to-native/references/solidworks-native.md) owns editable features,
origin constraints, rebuild/edit tests and saving. Read that workflow before operating
SolidWorks. For 2D extraction or STEP-only requests, do not impose native SolidWorks.

## Prepare a compact evidence handoff

| Item | What the next modeling step needs |
|---|---|
| Immutable source | Original path, revision/units and source hash when preserving a conversion input |
| Views | Identified orthographic/section views, orientation, scale and each view-to-model transform |
| Geometry | Analytic segments, loops, holes and relevant entity IDs for traceability within this drawing |
| Dimensions | Explicit callouts separately from measured vectors and inferred internal dimensions |
| Datum | Intended (0,0,0), axes, centered extents, fixed functional planes and expected edit behavior |
| Conflicts | Rounded labels vs vectors, general radii/chamfers vs actual edges, unresolved depths |
| Verification | Critical dimensions, hole count/locations, taper start/end sections and comparison tolerances |

Keep all supported source entities in the reconstruction evidence, but select the
actual views and model contours for construction. A classifier's group may still
contain a frame, dimension or symbol. Inspect it; do not extrude every group or use
the largest loop without determining what it represents. Manual selections can use
IDs/coordinates as provenance for this drawing; do not encode them as a reusable
classifier for the next drawing. Layer `0` is not a universal model-only filter.

Associate dimension text with its extension lines and view. Record a rounded nominal
label separately from its underlying vector measurement. When material differences
exist, apply the user's established source priority or resolve the ambiguity before
dependent modeling. Do not silently replace exact vectors with rounded values.
General R/C notes need an identified applicable edge set; defer ambiguous application
only when supported by the task/user decision, and record that decision for this part.

Reconstruct hidden depths only when the views and constraints provide support.
For a constant-angle draft, compare signed offsets with depth × tan(angle), including
which section opens wider. Label derived pocket depths, rib thicknesses and small
fillets as inferred when not explicitly dimensioned. The previous drawing's 0.5°,
R1/R2, R5 deferral, depths or material are not defaults for the next part.

## Close the loop after native construction

Use the same view-to-model transforms to compare saved-model projections to the
selected original vectors. Include rear/side/section evidence for drafted interiors;
one matching front silhouette is insufficient. Distinguish visible/hidden edges and
analytic vs sampled curves. State compared entity types/counts, exclusions, maximum
deviation, sampling error and the chosen diagnostic threshold. A projection match
does not prove unobserved internal geometry or native editability.

Inspect the overlays and 3D views, resolve material deviations, then let `$solidworks-dwg-to-native` finish
its native constraint audit, actual parameter-edit/restore tests, full-path save and
reopen verification. Hand off SLDPRT as the editing file, with assumptions and the
parameter guide; STEP remains exchange geometry.
