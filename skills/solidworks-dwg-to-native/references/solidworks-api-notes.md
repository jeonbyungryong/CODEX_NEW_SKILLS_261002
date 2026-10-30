# SolidWorks automation: observed API traps

Use alongside [the native workflow](solidworks-native.md). These observations were
exercised on SolidWorks 2022 SP5 (revision 30.5); confirm signatures, enums, templates
and resulting geometry on the installed version. They are recovery guidance, not a
universal macro or a reason to reuse another drawing's dimensions or entity IDs.

## COM and dimensions

- Strongly typed C# compiled with PowerShell `Add-Type` and the installed
  `SolidWorks.Interop.sldworks.dll` / `SolidWorks.Interop.swconst.dll` worked where
  late-bound PowerShell COM calls were unreliable. Discover actual installation
  paths and templates; avoid depending on localized plane/template names.
- Discover and bind the intended running application/document; avoid creating
  ambiguous instances. Use meters and radians at API boundaries.
- If suppressing the dimension-input dialog (`swInputDimValOnCreate`), record the
  prior setting and restore it in `finally`. Likewise restore temporary `AddToDB`
  state. Do not leave application-wide settings changed after an error.
- Query display dimensions and definitions rather than assuming every diameter is
  `D1` or has a particular localized name. Observed `IDisplayDimension.Type2` values
  were 11 horizontal, 12 vertical, 5 radius and 6 diameter for ordinary sketches;
  a wizard diameter used a different type. Match semantics and measured values,
  retain the actual dimension identity, then verify the equation changes geometry.

## FullyDefineSketch and coordinate frames

On tested line/circle sketches, selecting the actual origin as `EXTSKETCHPOINT`
with mark 6, then calling
`FullyDefineSketch(true,true,518,true,1,null,1,null,0,0)` achieved full definition.
Mask 518 combined coincidence/horizontal/vertical relations on this version;
`UseRelations=false` left sketches underdefined in that case. Resolve enum meanings
against the installed API, and use appropriate explicit constraints for other curves.
Do not treat this call as an all-profile recipe.

`ISketch.GetConstrainedStatus()==3` was the full-definition status. Verify it after
constraint creation, rebuild, parameter edits and reopening. Compare before/after
geometry. `GetRelations(0)` exposed fixed relations as types 17/70 in the tested
version; resolve the enum and distinguish authored sketches from wizard-generated
internal sections rather than recognizing them by a hard-coded sketch number.

Use `ISketch.ModelToSketchTransform` with `IMathPoint.MultiplyTransform` to map
world targets into sketch coordinates; use the inverse to check world positions.
Observed standard-plane orientations were front XY=world XY, top local Y=-world Z,
and right local X=-world Z. Face-based sketches can differ. Read the actual transform,
especially for mirrored rear faces, rather than hard-coding these signs.

## Hole Wizard

- `HoleWizard5` accepted a plain ISO drill hole with observed enum values hole type 2,
  standard 8 and drill type 143. These do not define every hole type or installation.
  Enumerate/confirm the required standard and size; do not copy a previous part's size.
- Unused numeric arguments set to zero succeeded in that case; substituting -1 in
  those slots returned null. Check the exact overload and argument semantics before
  changing defaults. Avoid blindly copying a long positional argument list.
- Four ray selections yielded only one position. Inspect the feature's subsketches:
  edit the location sketch, transform the intended coordinates, move/create the
  required points, then dimension them from the origin. Check world-space results.
- For the tested plain through hole (definition type 25), `ThruHoleDiameter` returned
  the actual size; `Diameter`/`HoleDiameter` returned zero. Use the property appropriate
  to the actual hole type and validate the resulting cylindrical/conical geometry.
- The wizard-generated section had one fixed anchor while the authored location
  sketch had none. Preserve the valid generated definition and report the distinction.

## Draft, body scope and combination

| Operation in tested orientation | Observed result | Verification required |
|---|---|---|
| `FeatureExtrusion3`, boss toward +Z, `Ddir1=false` | Exterior shrank with depth | Measure start/end sections |
| `FeatureCut4`, `Dir=true` toward +Z, `Ddir1=true` | Pocket/hole expanded with depth | Measure start/end sections |
| Same cut with `Ddir1=false` | Pocket shrank with depth | Establish rear opening and inner section independently |
| `InsertMultiFaceDraft`, rear neutral face, `FlipDir=true` | Mounting hole expanded toward front | Neutral face mark 1, draft faces mark 2; inspect sizes |

These flag outcomes depend on direction, plane and selection. A successful feature
or API description does not establish the final draft sign. Use section measurements.

For the tested rib-only cut, selecting the sketch with mark 0 and intended bodies
with mark 8 **before creation**, with `UseFeatScope=true` and `AutoSelect=false`,
worked. Assigning `FeatureScopeBodies` afterward did not produce the intended scope.
Track excluded bodies and compare their geometry/volume before and after the cut.

For a union, selecting intended bodies with mark 2 followed by
`InsertCombineFeature(15903,null,null)` worked; passing a body object array did not
in the tested case. Confirm the add-operation enum, body contact/overlap and final
topology. Any construction overlap must remain internal and must not alter the
specified visible shape; there is no universal overlap distance.

## Document identity and saved artifacts

Use `GetPathName()` as the identity check and exact file paths for lookup/open.
The tested 2022 flow was `GetOpenDocumentByName(targetPath)` or
`OpenDoc6(targetPath,...)`, then `ActivateDoc3(targetPath,...)`, followed by equality
of `ActiveDoc.GetPathName()` and `targetPath` before SaveAs. `CloseDoc(taskPath)`
closed the identified saved scratch copy in that environment. Inspect each method's
signature/behavior on another version: activation/closing name selectors are not
interchangeable with file-path lookup parameters. If a version resolves a selector
only by title, do not call it with an ambiguous duplicate title; resolve the intended
document through a supported API/UI path or unique task-owned working filename.
Stop export on identity mismatch. For an unsaved new part, track the document instance
and give it a unique native path first.

Duplicate open filenames in different folders caused open error 65536
(`swFileWithSameTitleAlreadyOpen`) and, separately, wrong-document STEP output despite
a successful SaveAs result. Close only known task-owned saved scratch copies or use
unique filenames; protect user edits. Verify the exact final native and STEP files.

`GetErrorCode2(out warning)` supports feature health checks. Walk top-level features
and absorbed subfeatures with deduplication; do not count or audit only visible tree
rows. Validate with rebuild/edit/reopen checks from the workflow. Keep return values,
warnings and geometry evidence separate in the report.
