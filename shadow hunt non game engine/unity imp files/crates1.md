Objective
Replace the current flat, repetitive, artificial-looking map floor with a convincing, high-quality industrial surface. The result should feel like a real, heavily used sci-fi facility floor under cinematic game lighting—not a tiled brown/black placeholder.

Scope is strictly flooring and floor lighting. Do not redesign the maze or change gameplay.
Non-negotiable constraints
- Preserve the current map layout, boundaries, dimensions, camera angle, scale, and playable area.
- Do not move, resize, replace, or redesign crates, walls, barriers, characters, guards, pickups, medkits, terminals, plants, UI, or other props.
- Do not change movement, collisions, pathfinding, enemy AI, vision cones, health, scoring, objectives, or any core gameplay logic.
- Do not bake the floor into a single background image. The floor must remain a real Unity scene surface with appropriate materials and lighting.
- Keep the existing art direction: dark industrial sci-fi facility, warm amber/orange practical lights, restrained cyan/blue accents.
- Avoid a uniformly glossy floor, exaggerated mirror reflections, obvious repeating patterns, noisy grunge, excessive bloom, or a flat orange overlay.
First: inspect the existing project
Before editing:
1. Identify the Unity render pipeline in use (Built-in, URP, or HDRP), current floor GameObjects/prefabs, floor materials, texture import settings, lights, and post-processing.
2. Find whether the floor is one large mesh, modular tiles, sprites, or a Tilemap.
3. Reuse the current setup where practical. Do not migrate render pipelines or install packages without a clear need.
4. Make a backup or use version control before changing shared materials.
5. Confirm the floor's current collision setup and preserve it exactly.
Visual target
Create a believable industrial floor made from large, heavy metal plates or reinforced facility panels:
- Deep charcoal / gunmetal base, not pure black or flat brown.
- Subtle panel seams, recessed joints, bolts, bevelled edges, drainage channels, and occasional grated service panels.
- Fine brushed-metal grain and restrained roughness variation.
- Localized wear: scuffs, scratches, boot marks, faded paint, small patches of grime, oil smudges, and edge wear.
- A few controlled hazard-painted markings near existing machinery or transitions, only where they fit the current layout.
- Slightly varied panel values and orientations so the floor does not look like a repeated checkerboard.
- Surface detail should remain legible at the game's actual camera distance. Avoid micro-detail that disappears or turns into visual noise.
- Keep the floor visually quieter than gameplay-critical objects. The player, guards, vision cones, collectibles, and obstacles must remain easy to read.
Material and texture requirements
Use a coherent PBR material rather than relying on color alone:
- Base Color / Albedo: dark neutral gunmetal with subtle variation.
- Normal map: fine metal grain, shallow seams, and restrained surface imperfections.
- Metallic: appropriate for industrial metal; do not set every surface to perfectly metallic.
- Smoothness / Roughness: varied by material region. Main walkable plates should be satin or semi-matte, with only small worn areas catching brighter highlights.
- Ambient occlusion: subtle contact shading around seams, bolts, grates, and panel edges.
- Use seamless/tileable textures with controlled UV scale. Inspect in-game for visible repetition and stretching.
- If using a texture set, keep albedo, normal, mask/metallic-smoothness, and AO aligned at the same scale.
- Prefer a small number of well-configured materials and shared textures over hundreds of unique materials.
- Use texture resolution appropriate to the floor's on-screen size and project performance; avoid needlessly huge textures.
- If the project is 2D or sprite-based, adapt the same material goals to the existing rendering approach instead of forcing a 3D conversion.
Lighting: make the floor feel grounded
Tune lighting on the floor only where possible:
- Use warm amber/orange pools from existing practical lights, with believable falloff and soft transitions.
- Add restrained cool cyan/blue fill in selected areas to complement the existing palette.
- Make lights illuminate the floor physically; do not simulate all lighting by painting orange or blue gradients into the albedo.
- Use soft, readable contact shadows beneath existing props and along wall/floor joins.
- Use baked or mixed lighting for static geometry if the project's current pipeline supports it and it is suitable; keep dynamic character/guard lighting and shadows working.
- If using URP, check the current renderer and lighting configuration before adding features. Do not assume screen-space reflections or HDRP-only features are available.
- If real-time reflection support is unavailable or too expensive, use subtle reflection probes where supported, or roughness-controlled highlights instead of fake mirror reflections.
- Keep exposure, bloom, and contrast restrained. Floor lights must not wash out the HUD or hide the vision cones.
- Avoid adding many overlapping real-time lights. Prefer reusing/tuning existing lights and using baked lighting for static areas when practical.
Implementation plan
1. Locate the floor objects/materials and document the current setup.
2. Create or refine a dedicated floor material without unintentionally changing unrelated objects that share the old material.
3. Apply the material to the existing floor geometry/tiles while preserving colliders and transforms.
4. Add or refine a small, consistent texture set and UV scale. Break up repetition with subtle variation between panels.
5. Improve the existing floor illumination and contact shading using the current render pipeline.
6. Keep grates, hazard markings, and special panels as separate modular details only where useful; do not clutter every tile.
7. Enter Play Mode and inspect the floor at the actual game resolution and camera zoom.
8. Check all existing paths and gameplay interactions remain unchanged.
9. Profile rendering if lights, transparent layers, or materials were added. Remove expensive changes that do not create a visible improvement.
Acceptance criteria
The task is complete only when:
- The floor no longer looks like a flat, repetitive, uniformly colored grid.
- The surface reads as real industrial metal at normal gameplay zoom.
- Panel seams, surface wear, and material response are visible but not distracting.
- Amber and cyan light pools look like illumination, not painted overlays.
- The floor has controlled highlights and roughness rather than a plastic or mirror-like sheen.
- Existing maze geometry, props, UI, camera, collisions, and all gameplay logic behave exactly as before.
- No pink/magenta materials, missing textures, shader errors, z-fighting, texture stretching, obvious tiling, or severe frame-rate regression are introduced.
Required final report from the agent
After implementation, report:
1. Which floor objects, prefabs, and materials were changed.
2. Which textures/material maps were reused or created.
3. Which lighting settings were adjusted and why.
4. Confirmation that maze layout, colliders, camera, UI, and gameplay logic were not changed.
5. Any remaining limitations caused by the project's current render pipeline or assets.
Do not expand scope. This task is only to make the existing floor look physically believable and properly lit.