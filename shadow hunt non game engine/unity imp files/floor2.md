# SHADOW HUNT — FLOOR REALISM PASS 2

## Objective

Refine the existing Unity map floor until it resembles a physically believable, heavily used industrial facility. The current floor still looks like a uniform square grid with a scratched overlay and an orange tint. Correct those specific problems.

**Modify ONLY the existing floor materials, floor textures, floor surface details, and lighting that directly affects the floor.**

## 1. Preserve the Existing Game

Do not change:
- Maze layout, dimensions, or playable paths.
- Crates, barriers, walls, guards, player, collectibles, or props.
- Camera, HUD, UI, health, scoring, AI, collision, movement, or game algorithms.
- The existing game art direction or level composition.

Do not replace the game with a static image or use a single baked screenshot as the floor.

## 2. Remove the Artificial Grid Appearance

Inspect the current floor mesh, UVs, material, and texture tiling.

- Reduce the visual dominance of the repetitive square grid.
- Replace the uniform checkerboard appearance with larger, believable industrial steel panels.
- Use recessed seams between panels, with subtle bevel shading and restrained fastener details.
- Vary panel size, roughness, wear, and brightness subtly, while keeping a coherent modular floor layout.
- Do not simply hide every seam. Seams should remain visible at gameplay zoom, but must not dominate the image.
- Eliminate obvious repeating scratches, identical stains, and mirrored texture patterns.
- Correct stretched textures, incorrect UV scale, z-fighting, and overlapping surfaces.

If the current floor is a Unity Tilemap or modular grid, preserve its structure and use materials, texture variation, or appropriate surface meshes to improve its appearance. Do not rebuild the maze.

## 3. Make the Material Physically Believable

Use the rendering pipeline already installed in the project.

Create or refine a coherent PBR material using:
- Dark neutral gunmetal base color with subtle tonal variation.
- Fine brushed-metal grain and realistic, irregular scuffs.
- Localized grime near seams, corners, machinery, and frequently traversed areas.
- Sparse oil marks and worn paint, without covering the entire floor in grunge.
- Correct normal or bump detail for shallow scratches and panel joints.
- Appropriate metallic and smoothness values, with varied roughness across the surface.
- Subtle ambient occlusion around recessed joints and contact areas.

Avoid pure black surfaces, flat brown overlays, plastic-looking gloss, and perfectly mirrored reflections.

The walkable floor should be mostly satin or semi-matte metal. Only selected worn or smoother areas should catch stronger highlights.

## 4. Correct the Lighting

Make the existing floor respond convincingly to light.

- Retain warm amber/orange practical lighting and restrained cyan/blue accents.
- Create localized illumination with natural falloff rather than a uniform orange wash.
- Preserve dark areas between light sources to give the scene depth.
- Add believable contact shadows beneath existing crates and along wall-floor joins.
- Keep emissive strips bright enough to appear powered, but prevent them from washing out the surrounding surface.
- Use baked or mixed lighting for static environment elements where supported and appropriate.
- Reuse and tune existing lights before adding new real-time lights.
- Use reflection probes or supported reflection features only where suitable for the current pipeline and performance budget.
- Keep the floor rough enough to avoid a wet-plastic or mirror-like appearance.

Do not paint lighting gradients into the albedo as a substitute for actual illumination.

## 5. Match the Actual Camera

Evaluate the result in Play Mode using the current camera and actual gameplay resolution.

The floor must read as a realistic industrial surface from the normal gameplay view, not merely look detailed when zoomed in.

At normal zoom:
- Panel joints should be clear but restrained.
- Wear should be visible without becoming visual noise.
- The floor should have depth, material variation, and convincing light response.
- The player, guards, vision cones, pickups, and maze obstacles must remain immediately readable.

## 6. Technical Requirements

- Identify whether the project uses Built-in, URP, or HDRP before changing shaders.
- Reuse existing assets where they genuinely improve the result.
- Avoid unnecessary packages, render-pipeline migration, or expensive per-tile materials.
- Use shared materials and appropriate texture resolution.
- Preserve all existing floor colliders and object transforms.
- Check for missing textures, pink shaders, UV stretching, visible tiling, and performance regressions.

## 7. Acceptance Test

Do not consider the task complete merely because the floor has more scratches or a different color.

The result must visibly improve in these areas:
1. Less repetitive grid appearance.
2. More believable steel plate construction.
3. More natural and irregular surface wear.
4. Proper material response and roughness.
5. Localized amber and cyan illumination with natural falloff.
6. Better contact shadows and separation between floor panels.
7. No changes to gameplay, maze geometry, UI, or props.

Compare the result with the original screenshot at the same resolution and camera zoom.

## Final Report

Explain:
- What caused the artificial grid appearance.
- Which floor materials, textures, UVs, and lighting settings were changed.
- How the improvements were verified in Play Mode.
- Whether the project has any rendering limitations.

Do not expand scope beyond floor realism.
