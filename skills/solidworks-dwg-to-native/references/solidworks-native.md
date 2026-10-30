# Editable native SolidWorks from drawings

Read for native SLDPRT deliverables, particularly DWG/DXF conversion with origin-based
fully constrained sketches. For automation, also read [API notes](solidworks-api-notes.md).
This route supplements cadgen; build123d can independently inspect exported geometry
but cannot substitute for a native editable SolidWorks feature history.

## Define the model contract

Before construction, record these task-specific decisions:

| Field | Required content |
|---|---|
| Source | Exact path, units, revision, view/section interpretation; preserve original |
| Evidence | Explicit dimensions, measured vectors, inferred depths and unresolved conflicts |
| Coordinates | World axes, origin, principal planes, functional datum, world-to-sketch transforms |
| Centering | Which extents are centered initially, and which datums remain fixed after edits |
| Features | Sketch/boss/cut/Hole Wizard/fillet/draft plan and controlling dimensions |
| Editable parameters | Names, nominal values, dependencies, representative changes to verify |
| Validation | Dimensional and projection tolerances, body count, expected constraints and outputs |

For origin-centered drawing conversion, use the requested center as (0,0,0), with
mid-plane extrusions and symmetric dimensions where appropriate. An asymmetric part
may need a functional datum instead; follow the user's specified datum. State this
choice explicitly. Initial bounding-box centering does not imply that all three
extents stay centered after a one-sided boss-height edit. Keep the intended datum
fixed and verify the expected movement, rather than translating the result afterward.

Respect the chosen source priority. Rounded dimension labels, exact vectors and
general R/C notes can disagree. Resolve material conflicts from available evidence
and user direction. Do not silently round vectors or apply a general fillet to all
edges. A decision to defer R5 on one drawing is not a rule for other drawings.
Geometry inferred from draft or orthographic projections remains an assumption.

## Build editable features and constraints

1. Create a native part using an installed template; confirm document units. API
   lengths commonly use meters even when the user works in millimeters.
2. Create sketches in known planes and transform world coordinates into each sketch's
   frame. A rear-face sketch may reverse an axis. Do not copy screen coordinates or
   assume every sketch's XY frame equals world XY.
3. Reference the actual origin or deliberately constrained construction geometry.
   Use dimensions and coincidence, horizontal/vertical, symmetry, concentricity and
   tangency as justified by geometry. Numeric creation coordinates alone are not
   constraints. Do not blanket-Fix imported contours to obtain a fully defined status.
4. Give meaningful dimensions and features names; expose useful global variables and
   link dependent dimensions with equations. Preserve design relationships such as
   center symmetry, edge margins and concentric bores when variables change.
5. Use native bosses/cuts for profiles, appropriate native Hole Wizard features for
   standard holes, and native fillet/draft features where appropriate. Nonstandard
   ports and keyways may use dimensioned sketch cuts. Do not force every opening into
   Hole Wizard or claim an imported body is an editable feature model.
6. Inspect actual feature definitions, geometry and dependency order. Verify merging,
   body scope and taper direction after the affected operation, before building on it.

Fully defining a sketch can move geometry. Capture defining points/centers/radii
before and after automatic constraints and compare within the task's numerical
tolerance. Inspect each sketch's actual constrained status, including absorbed
subfeatures. A helper returning success is insufficient. For curves, verify intended
tangency/continuity as well as status; an indiscriminate auto-relation mask can alter
the source contour or overconstrain it.

Report custom sketch Fix relations separately from native wizard internals. A wizard's
generated section can legitimately contain an internal fixed anchor. Its location
sketch still needs origin/datum dimensions. Do not remove that anchor just to claim
"zero Fix relations," and do not use it to justify fixing the authored geometry.

## Hole Wizard and scoped operations

- Confirm the supported standard/type/size on the installed version. A non-null
  feature alone does not establish the intended diameter, termination or locations.
- Count actual location points. Multiple face/ray selections can still create a
  single point. Edit the wizard location sketch, transform desired world positions
  into its local frame, add missing points and constrain them to the origin/datum.
- Transform the completed points back to world coordinates and verify count, axes,
  spacing and depth. Read the relevant diameter/termination from the definition;
  different hole types expose different properties.
- For cuts that should affect only ribs or other selected bodies, set selection marks
  and feature scope during creation. Verify excluded bodies remain unchanged. A later
  property assignment that returns without error is not proof of correct scope.
- Merge intended bodies deliberately and verify the expected final body count. Do not
  use bounding-box or volume thresholds from a previous part to identify new bodies;
  use tracked feature results and the current part's geometric evidence.

## Determine draft direction geometrically

Compute the expected section sizes at the start and end of a taper. For a simple
constant-angle wall, the signed offset is depth × tan(angle); establish the sign
from the intended pull direction and cavity/boss geometry. Measure both sections.
Do not infer the resulting sign from a Boolean flag's name alone.

A matching front projection does not validate a rear pocket. Compare the relevant
front, rear and side/section geometry. A reversed taper can preserve one silhouette
while changing internal walls. Correct the responsible feature and repeat affected
constraint, edit and saved-geometry checks.

## Verify editing, saving and exports

Record actual results for the following gates, proportionate to the feature set:

1. **Native baseline:** expected solid count, positive volume, bounds/datum, feature
   errors and warnings, constrained status for every authored/absorbed sketch, custom
   Fix count separately from generated wizard anchors, no imported feature replacing
   the required native construction.
2. **Actual edits:** change each exposed controlling variable within a meaningful
   range; also exercise a representative combined change. Force a rebuild and inspect
   the resulting geometry, constraint status, hole centers/diameters and datum behavior.
   Merely changing an equation string or observing a changed volume is insufficient.
3. **Restore:** restore nominal parameters even if a test fails. Rebuild, compare the
   restored dimensions/geometry, save, close the exact task document and reopen the
   saved SLDPRT. Confirm identity and repeat baseline checks. Do not close or discard
   unrelated user documents or unsaved edits.
4. **Export identity:** identify documents by full path, not title. Before an export,
   explicitly activate the intended document and compare the active full path with the
   target. Same-title files in different folders have caused a successful export call
   to write another document's geometry. Prefer unique working filenames. Check the
   save return value, error and warning outputs, then independently open the saved file.
5. **Independent geometry:** inspect the final STEP's validity, solid count, extents,
   critical holes/sections and volume against the native result using stated tolerances.
   Sum individual solid volumes if a compound wrapper reports zero. Account for split
   circular edges when counting holes: group matching center/radius/plane evidence;
   do not count every edge as a distinct hole or hide missing geometry by deduplication.
6. **Drawing comparison:** compare selected source vectors with matching projected
   model edges in a common coordinate frame. Label visible/hidden edges, sampling or
   curve approximation error, entity types/counts and excluded geometry. A diagnostic
   threshold such as 0.05 mm is not automatically a manufacturing tolerance. Inspect
   overlay images and a saved-artifact 3D snapshot yourself. For native-only delivery,
   reopen the saved SLDPRT and inspect a screenshot from SolidWorks through the supported
   computer-use tools, including the tree and useful views. Do not export STEP solely
   to satisfy a snapshot rule. When STEP is delivered, review that saved export too.

File existence, SaveAs success, a screenshot, or fully defined status alone cannot
establish all these gates. Report failures and assumptions rather than calling them
verified. After a geometry repair, rerun the checks it can affect; do not repeat an
unchanged full test suite solely for ceremony.

## Handoff

Deliver the native SLDPRT as the editing entrypoint, plus STEP when useful, a concise
parameter/feature guide, checks actually executed and source-generation code if used.
Explain units, datum behavior, inferred dimensions and observed edit ranges. Recording
a material grade/color as a custom property is not assigning validated physical material
properties. Open the final delivered path and verify its native tree and geometry.
Preserve originals and previous results. If an open file prevents hashing/copying,
save and close only the task-owned document, then copy and compare hashes before
reopening the final copy. Do not force-close the entire CAD application.
