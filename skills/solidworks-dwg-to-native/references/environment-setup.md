# Per-PC readiness and first-use verification

Check the current PC; do not copy the author's username, executable paths, templates,
sample drawings or document names. This package contains instructions and reconstruction
helpers, not a CAD engine, application license, generic automatic 3D inference engine,
or preconfigured MCP server. Do not silently install software or alter CAD settings
as part of a skills-only installation.

## Required for the SolidWorks route

- Windows with a usable licensed SolidWorks installation and an available part
  template. Confirm the actual application/API version and access to its native API
  or supported computer-use surface. The recorded COM observations were tested on
  SolidWorks 2022 SP5, not all versions.
- For DWG extraction: an installed ODA File Converter, or an available CAD application
  such as AutoCAD that can export a separate DXF copy. AutoCAD is not required when
  ODA is available. Preserve the original DWG; successful DXF export is not 3D modeling.
- Python 3.12+ and `uv` for the bundled image-to-cad scripts. Their inline dependency
  metadata provisions an isolated environment when executed with `uv run`; the first
  execution may download dependencies. Merely installing the skill copies files.
- Optional independent STEP validation/snapshots: the installed `$cad` skill's
  cadgen environment. Use its pinned version and runtime instructions when needed.

Read-only discovery can use `Get-Command uv,python -ErrorAction SilentlyContinue`,
Windows installed-application/COM registration and the existing CAD session. Discover
SolidWorks interop DLLs and template paths from that installation; do not assume an
English plane name, fixed Program Files directory or another PC's template name.
Do not launch or attach a second ambiguous CAD instance when the intended session
can be identified. Preserve open user documents and unsaved changes.

## Reconstruction commands

Resolve the installed `image-to-cad` skill directory from the available-skills list,
then run from that directory or use absolute script paths:

```powershell
uv run scripts/validate_samples.py
uv run scripts/reconstruct_geometry.py --input <drawing.dwg> --output-dir <new-output-folder> --dwg-converter <installed-ODA-executable>
```

`--dwg-converter` is explicit. The script also searches the current PC's ProgramFiles,
ProgramFiles(x86) and LOCALAPPDATA ODA directories and accepts `EPDM_DWG_CONVERTER`.
If ODA is absent, use an authorized installed CAD application's DXF export. Do not
claim DWG support from a successful DXF-only test. The vector path also accepts DXF
directly without ODA. Raster physical units require supplied calibration.

## First use on another PC

1. Confirm the skill list contains both `image-to-cad` and `solidworks-dwg-to-native`;
   inspect same-name local customizations before installing/updating. Install both
   complete folders so their references and helpers remain available.
2. Run the synthetic reconstruction sample in a disposable directory. This checks
   Python/vector processing, not the CAD license, COM or real DWG converter.
3. With the user's modeling authorization, build a small disposable native part with
   an origin-dimensioned sketch, extrusion and standard hole. Verify actual constraint
   status and a dimension edit/rebuild/restore, then save and reopen it. Record the
   application version and failed capabilities.
4. Process the requested drawing and execute its geometry-specific validation. The
   synthetic part does not prove interpretation of an arbitrary engineering drawing.

If CAD access is unavailable, finish source/evidence inspection and report the concrete
missing dependency. Do not label an imported solid or a STEP-only file as an editable
SolidWorks feature model. For another native CAD application, map the same design
intent/verification contract to its supported features; verify it independently and
report that application's actual tested scope.
