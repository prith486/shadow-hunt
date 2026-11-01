Objective
Upgrade the six existing crates so they look like rugged, authentic, dimensional industrial cargo containers—not flat wooden squares with a few added scratches. Match the realistic 3D industrial style of the supplied reference image and the already-enhanced metal floor.

Only refine the six existing crates. Preserve their exact footprint, world positions, gameplay role, and collision behavior.
Critical scope lock
Do not modify the floor, walls, maze layout, surrounding environment, player, guards, pickups, medkits, barriers, UI, camera, or core algorithms. Do not change health, score, targets, movement, AI, line-of-sight, collision logic, or level progression.

Do not replace the scene with a static image. The crates must remain real Unity scene objects with appropriate meshes/materials and working colliders.
First inspect the current implementation
1. Locate all six crate GameObjects or prefabs and identify their meshes, renderers, materials, transforms, colliders, and shared assets.
2. Determine whether each crate is a flat sprite, a top-only mesh, a cube with a texture, or a 3D model.
3. Inspect the current Unity render pipeline and existing floor material/lighting.
4. Record the exact world-space footprint, height, position, rotation, and collider bounds of each crate.
5. Back up or version-control affected assets before editing.
6. Reuse existing crate objects and gameplay components wherever possible.
Do not assume the current objects are real 3D models. Confirm this in the project.
Visual target: rugged, dimensional industrial crates
1. Real three-dimensional shape
- Give each crate visible vertical side walls and a substantial base/skirt, not merely a decorated flat top.
- Use modest bevels or chamfered edges to catch light naturally.
- Add visible thickness to the lid, frame rails, diagonal braces, and corner brackets.
- Add small but clear height differences between the top panel, reinforcing braces, central plate, and outer frame.
- Use real mesh geometry for major structural elements where practical. Do not fake all depth with painted highlights.
- Ensure side faces and contact shadows are visible from the current camera angle.
- Preserve the original crate footprint. If visual height is improved, keep the gameplay collider unchanged.
2. Upper row: rugged brown/orange crates
Retain the existing three upper-row crates and their brown/orange identity:
- Weathered timber or industrial composite planks with visible grain, dents, scratches, chipped edges, and slight plank-to-plank variation.
- Dark gunmetal perimeter frame with thick corner guards.
- Substantial diagonal X-braces with visible thickness, attached by bolts or rivets.
- A central metal junction plate with beveled edges and restrained wear.
- Heavy steel corner caps with screws/bolts and realistic metallic highlights.
- Small inset orange emissive strips only where they suit the current design; do not add excessive neon.
- Existing amber diamond markings should remain aligned to the top surface and should not look like floating UI icons.
3. Lower row: rugged military-green crates
Retain the existing three lower-row crates and their olive-green identity:
- Chipped olive-drab painted steel or reinforced composite panels, with subtle exposed metal at worn edges.
- Thick dark metal perimeter rails and diagonal X-braces.
- Beveled central plates, visible bolts, corner caps, and reinforced base trim.
- Existing pale stencil markings should look like worn paint applied to the surface, not raised white objects.
- Use subtle grime and scratches, avoiding excessive rust or random damage.
- Keep the three green crates stylistically consistent with one another and with the brown crates.
4. Side panels and base
- Add side-panel structure with recessed sections, horizontal reinforcement ribs, industrial vents, fasteners, and restrained hazard markings where visible.
- Include a dark reinforced bottom skirt or base frame to visually ground each crate.
- Give the base a believable contact shadow on the floor.
- Keep side detail low enough in contrast that it does not compete with the top surface.
- Do not add handles, protrusions, or decorative parts that extend into adjacent walkable paths or change gameplay.
Materials and lighting
Use the project's existing render pipeline. Do not migrate pipelines.
- Use appropriate PBR materials: albedo/base color, normal map, metallic response, and smoothness/roughness.
- Brown crate planks should have convincing wood/composite grain and a mostly matte finish; metal framing should be rough, worn gunmetal.
- Green crates should have a chipped painted-metal or painted-composite surface, with subtle exposed metal on edges.
- Avoid uniformly glossy materials, plastic-looking surfaces, perfectly clean edges, and exaggerated mirror reflections.
- Match the floor's amber/orange practical lighting and restrained cyan accents.
- Let existing lights illuminate the new geometry naturally. Add or tune only minimal crate-focused lighting if genuinely required.
- Use contact shadows and ambient occlusion where supported to separate braces, plates, side walls, and the floor.
- Avoid excessive bloom, overbright emissive strips, or strong glow that obscures crate geometry.
- Check normal-map import settings and material channel conventions for the current pipeline.
Six crates: variation without inconsistency
- Keep the same three brown crates on the upper row and three green crates on the lower row.
- Introduce only subtle variation in plank wear, scratches, stencil wear, and small surface marks.
- Do not randomly rotate or reposition the crates.
- Preserve current distinctive top markings and color coding unless a small material adjustment is necessary for realism.
- Ensure each crate has consistent proportions, structural thickness, corner hardware, and lighting response.
Technical implementation rules
- Preserve each existing GameObject's position, rotation, scale, and gameplay components unless a change is explicitly required for visual-only child meshes.
- Prefer a visual-mesh child under the existing crate root if that improves the model without changing gameplay transforms.
- Keep gameplay colliders on their existing roots and verify their bounds remain unchanged.
- Do not let new mesh parts extend beyond the existing gameplay footprint or block neighboring corridors.
- Avoid unnecessary high-poly geometry, unique materials per bolt, or excessive real-time lights.
- Use shared materials and instancing where appropriate.
- If importing external models or textures, ensure they are available/licensed and do not add dependencies without need.
- If a fully custom model is unnecessary, improve the existing mesh and materials rather than replacing the entire asset pipeline.
Validation in Unity
Test in Play Mode at the real gameplay camera and resolution. Verify:
1. All six crates have visible thickness and credible side faces.
2. Top braces, corner caps, bolts, and central plates have real dimensional separation.
3. Brown and green materials look rugged and physically distinct.
4. Crates remain clear and recognizable at normal gameplay zoom.
5. No geometry clips into neighboring objects or walkable paths.
6. Original colliders, positions, movement, pathfinding, and line-of-sight behavior remain unchanged.
7. Existing UI, floor, guards, player, pickups, and barriers are untouched.
8. No missing textures, pink materials, shader errors, z-fighting, excessive glow, or serious performance regression appears.
Compare a screenshot before and after at the same camera angle and resolution.
Acceptance criteria
Do not mark the task complete just because scratches or glow have been added.

The result must visibly read as six heavy, rugged, three-dimensional industrial cargo crates, with thick frames, layered construction, beveled metal hardware, believable materials, side depth, and grounded shadows—while retaining the same size, placement, and gameplay behavior.
Required final report
Report:
- Which crate prefabs/GameObjects and visual meshes were changed.
- Which materials, texture maps, and geometry details were created or reused.
- Confirmation that all six footprints, positions, colliders, and gameplay logic remain unchanged.
- Any compromises required by the existing camera angle or render pipeline.
Scope ends at the six crates. Do not modify anything else.