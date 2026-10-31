# Shadow Hunt — Godot 4 port

This is a native Godot 4/GDScript migration of the Shadow Hunt Unity project. It implements three playable levels, player movement and melee combat, Boar King and shielded Shaman King guards, the Devil Leader boss, Mommy's house nightmare, pursuit and patrol behavior, hiding spots, barricade cover, security-camera detection, sliding doors, collectibles, extraction/alarm states, campaign statistics, HUD/menu flow, and the custom computer-graphics algorithms.

## Run

Open this folder in Godot 4.x and run `Main.tscn` (or press **F6** with `Main.tscn` selected). The window is configured to the Unity project's 980 × 820 resolution. No third-party addons are required.

## Controls

- **WASD / Arrow keys:** move (moving also exits a hiding spot)
- **Shift:** sprint (guards can hear sprinting)
- **Ctrl / J:** jump
- **Space:** one-hit sword attack (plays the player attack frames; the Shaman King's front shield blocks frontal hits)
- **E:** quietly open a nearby blue glass door; hold **E** while moving to move slowly
- **Left-click a marked hide spot while nearby:** hide; click it again or move to leave
- **Level 3 MIC toggle:** optionally enable live microphone-level detection
- **H:** toggle CG hitbox overlay
- **R:** retry the current level
- **Enter:** advance after completing Level 1 or 2
- **Esc:** return to the main menu (or quit from the menu)

Guards pursue the player while they can see them and search the last-seen position for 3.5 seconds after losing sight. They shoot visible players: Boar King bullets remove 5 health points, and Shaman King bullets remove 10. The lockdown timer is shown in the center of the screen with a pulsing red overlay. Defeated guards disappear immediately and drop a blue diamond worth 250 points/coins. Extraction is available whenever the player reaches the exit; eliminating every guard first earns the clean-extraction bonus. Level 2 is available for direct entry from the main menu, matching the Unity build. A Level 1 extraction unlocks the campaign's next-level flow. Career score, coins, and eliminations are stored in Godot's `user://career.cfg`.

Level 3 uses Level 2's arena dimensions, crates, and doors, with the four short wall segments that obstruct its walking lanes cleared. Its wider scrolling camera follows the player and clamps at the arena and house boundaries, keeping the map clipped to the viewport. Three guards and the Devil Leader roam the arena. The Devil Leader is 1.5 times the normal enemy render size and shoots projectiles that remove 25 health points per hit. After each of three sword hits, the boss blinks out for one second, reappears elsewhere, and runs for 1.2-2 seconds before resuming his patrol. Three segmented dashes show the remaining hits. The final hit triggers a brief black transition into the one-minute Mommy house stage.

The Mommy house follows the supplied floor plan: four bedrooms across the upper-left wing, storage, tiled bathroom and laundry rooms, the lower-left fireplace living room, a central hall, a tiled kitchen/dining room, and the main exit at the bottom. Mommy patrols all ten rooms in a randomized order and keeps moving instead of waiting in the passage. If she spots Freenight, she follows him even after briefly losing sight; hiding breaks pursuit and makes her search around his last-seen position before resuming her patrol. Mommy attacks at close range; being caught automatically restarts the Nightmare level. She also investigates loud sounds such as broken glass, footsteps, bumped furniture, and glass shards. Blue glass doors can be quietly opened with **E** (holding **E** while moving slows movement); pushing/running into one shatters it, creates debris, and alerts Mommy. Walking over the debris emits additional crunching noise. Furniture is visual cover and does not block the player or Mommy, while house walls and doors preserve the room boundaries. The main doorway is marked **EXIT** and is the only way to leave the house before the timer expires. Click a marked wardrobe, bed, laundry appliance, fridge, or sofa hiding spot while nearby; moving or clicking the active spot again exits hiding. Staying in one hiding spot for more than ten seconds reveals its location to Mommy, so move to a different spot.

The three Mommy voice clips play in order—sweet at the start, mildly irritated after 20 seconds, and angry after 40 seconds. Processed copies in `assets/audio for mom/processed` trim the first two and last three seconds, remove longer quiet gaps, apply a low-frequency noise filter, and normalize the voice level. The supplied `little angry.ogg` and `angry.ogg` files are identical, so the processed irritated clip is slightly faster/higher and the angry clip slower/lower to distinguish the two states. Suspense music plays under the sequence and a heartbeat joins during the last ten seconds.

Microphone monitoring is **off until enabled with the MIC toggle** in the house stage. It displays a 0–100% live input-level meter; the red marker indicates its 3% alert threshold. Above that threshold, Mommy turns red, investigates Freenight's current location, and the supplied `alexis_gaming_cam-the-suspenseful-braam-334309.mp3` plays. Input is measured in memory only; the game does not record, save, or upload microphone audio. A missing microphone leaves the feature disabled and emits a warning.

The project uses the available knight animation set in `assets/Characters/png` for the player, plus the Boar King and Shaman King directional sequences for the guards. The files do not identify the knight as “Freenight” by name.

The startup self-checks exercise affine rotation, line clipping, Bresenham circle, point-in-polygon, and spawn, patrol, and hiding-spot walkability across the four playable-stage layouts.

Run the focused Level 3 regression checks with `godot --headless --path . --script res://scripts/level3_revision_test.gd`.
