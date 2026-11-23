# Chongqing district continuation

- Active local scene is R24 market frontage build 08. Open `work/scene_r24/chongqing_district.blend` with Blender 4.3.2. The main Godot 4.6.3 project uses the preserved previously authored layers plus `assets/frontage_r24/frontage.glb`, the original mesh replacements and the resident animation library. Current commands are in `work/verify_frontage_r24.ps1`. Keep the R23 walk failure, block-edge flyover evidence, and projected ODbL source data with the changes. Geometry and artistic review remain local to the named sites. The entries below are historical.

- Previous local street study was R23. Open `work/scene_r23/chongqing_district.blend` for the editable district and `work/project/chongqing_godot_v05/project.godot` for the running project. The R23 layer is `assets/block_r23/block.glb` plus its donor manifest, routes, walking bodies and traffic models. Godot still composes all preserved base layers.
- Read the game’s `docs/STREET_R23_REVIEW.md` and the current handoff before further work. The nine original player images are in `work/scene_r23/user_evidence`. `work/verify_street_r23.ps1` runs the engine checks on the active project. Capture geometry, collision, input and image evidence separately. Keep R23 methods provisional until the player accepts the street in motion.

- R22 district environment build 07 is the previous baseline. The editable city is the geometry from build 06. Build 07 installs 32 validated high-quality GPU texture imports. Read START.md, HANDOFF_LOG.md and the game's docs/DISTRICT_R22_REVIEW.md before resuming. Keep the existing character and inspect the district from actual pedestrian height.
- Open `work/scene_r22/chongqing_district.blend` for the whole editable city. The independent layers are `roofs_and_breakfast.blend` and `river_context.blend`. Godot defaults to `assets/render_profile_r22.json`. Use `work/verify_roofs_r22.ps1 -Run import01` and the game's `verification_r22/import01` for build 07. Build 06 has an immutable checkpoint and its evidence in `verification_r22/current`. Keep OpenStreetMap attribution and derivative database alongside the bridge and shoreline.
- R21 build 07 is the previous district baseline, with its sources in `work/scene_r21` and evidence in `verification_r21/current`. The underlying R17 GLB, R19 street and R20 upper lane remain distinct inputs.

- R20 build 12 changes screen-space ambient occlusion sampling over the exact build 11 city and resident sources. Keep the full/half/full comparison, twelve in-engine fixed views and the native motion comparison in `verification_r20` when changing scene lighting.

- The tree-court resident has a separate editable rig in `work/characters/court_resident/court_resident.blend`. Keep its source license, seated-motion inputs, terrain fit and continuous in-engine take together with the environment. For shoe contact, inspect the deformed soles against the sloped paving.

- Active R20 city source: `work/scene_r20/chongqing_district.blend`. Godot composes the preserved base, R19 street layer and R20 upper lane under `render_profile_r20.json`, and installs the spatial meter meshes. Use `work/verify_lane_r20.ps1` and `verification_r20/current`. The full Blender scene retains the editable original meter geometry.

- Active workspace moved by full, non-destructive copy to `C:/Users/尹久/Documents/重庆外卖王` on 2026-11-20. The old Codex workspace is a retained historical copy, not the development target.
- Latest user rejects R17 appearance: rigid apron, unattractive default character, zombie motion. Continue internal visual iterations until the user asks for results. Do not treat a regression pass, revision number or progress screenshots as delivery or stop criteria.

This workspace continues the existing 200 × 200 m Chongqing project from v05/R15.
The user authorized local development on 2026-11-20 after cloud recovery inspection.

- Preserve `outputs/R15原始资产` as immutable original delivery archives and evidence. Never edit the user's Downloads project.
- Current working sources: `work/project/chongqing_blender_v05`; Godot: `work/project/chongqing_godot_v05`.
- First read START.md and the current handoff log. Keep authored Blender source, exported GLB and runtime logic versioned together.
- Baseline: Godot 4.6.3 Forward+, Blender 4.3.2. Do not silently upgrade to the user's installed Godot 4.7.2.
- R19 scene work: current whole-city editable composition is `work/scene_r19/chongqing_district.blend`; the reusable layer is `work/scene_r19/street_life.blend`. Runtime composes the preserved R17 city GLB with `assets/street_r19/street_life.glb`, its replacement manifest and `render_profile_r19.json`. Never relabel the base GLB as a new whole-city export.
- Scene art needs fixed-camera comparisons, close views, geometry/contact inspection, route checks and independent GPU sampling. A lighting-only change, asset count or passing tests cannot establish cinematic quality. Preserve rejected trials and their defects.
- Prior acceptance reports are historical evidence. New geometry and code require new tests and screenshots.
- Every claim must state its scope: inspected, implemented, imported, executed, visually reviewed, or unverified.
- Do not overwrite baseline hashes or relabel historical images as current captures. Do not claim background execution after the active session ends.
- Preserve source licenses. Record exact asset source, license, authors, modifications and downloaded hashes before integration.
- Work autonomously on routine decisions. Do not delegate to agents unless explicitly authorized by the user.
- Package a versioned game deliverable only after opening that exact candidate; preserve unresolved issues in the handoff.
- User steering on 2026-11-20: do not hurry to package. R16a is an internal checkpoint, not a delivery. Continue independent iteration toward cinematic image quality and substantial gameplay; tests passing is not artistic acceptance.
- User grants routine project permissions by default. Do not ask again for downloads, edits or engine runs; mandatory platform permission gates still apply and must not be bypassed.
