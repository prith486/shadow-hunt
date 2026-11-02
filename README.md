# SHADOW HUNT — Stealth Tactical Assassin & Horror Game

**Shadow Hunt** is a 2D top-down stealth action and horror survival game built with **Godot 4.x (GDScript)**. It features tactical stealth takedowns, custom computer-graphics algorithms (ray-casting field of view, 2D lighting, Bresenham line tests), multi-phase boss combat with the Warden, and an atmospheric mic-enabled Nightmare survival level with Mommy.

---

## 🎮 Quick Start & How to Play

### Option 1: Direct Double-Click (`.exe`)
- Simply double-click **`ShadowHunt.exe`** in the root directory.
- The game launches immediately as a native standalone application.

### Option 2: Batch Launcher (`.bat`)
- Double-click **`run_game.bat`**.
- It detects local dependencies and launches the game directly.

### Option 3: Godot 4 Editor
1. Open Godot Engine (v4.3+ / v4.7+).
2. Click **Import** and select `HunterAssassinGodot/project.godot`.
3. Press **F5** (or click **Play**) to run the project.

---

## ⌨️ Controls & Input Mapping

| Action | Key / Control | Description |
| :--- | :--- | :--- |
| **Movement** | `W`, `A`, `S`, `D` / Arrow Keys | Move Operative in 8 directions (also exits hiding) |
| **Sprint** | `Shift` (Hold) | Sprint at $1.6\times$ speed (produces audible footsteps) |
| **Silent Walk** | `E` (Hold while moving) | Sneak quietly with reduced footstep radius |
| **Melee Attack** | `Space` / Left Mouse Button | Instant takedown from behind; strikes in facing direction |
| **Jump / Hop** | `Ctrl` / `J` | Jump hop over ground clutter and floor obstacles |
| **Hide Interaction** | Left Click on Spot / Walk Into Spot | Hide in Wardrobes, Laundry, Fridge, Sofa |
| **Quiet Glass** | `E` near glass doors | Open glass door quietly without shattering |
| **Microphone Input** | Real-time USB / Built-in Mic | Live voice level meter detects speech during Nightmare level |
| **Debug Overlay** | `H` | Toggle debug hitboxes, paths, vision cones, and audio meters |
| **Restart Level** | `R` | Quick restart current level |
| **Pause / Menu** | `Esc` | Pause game and open level navigation menu |

---

## 🗺️ Levels & Mission Overview

### 🔹 Level 1: Infiltration (The Compound)
- **Objective:** Eliminate patrolling security guards and extract through the gate.
- **Enemies:**
  - **Patrol Guards:** Armed with vision cones ($90^\circ$ FOV) and laser rifles.
  - **Enforcers (Shielded):** Equipped with a front-facing energy shield that blocks frontal takedowns and projectile fire. Strike them from behind!
- **Mechanics:**
  - Dynamic line-of-sight vision cones.
  - Hiding spots (Wardrobes, crates) that break enemy pursuit.
  - Security cameras scanning zones; triggering alarms summons facility lockdown.

### 🔹 Level 2: Boss Arena (The Warden)
- **Objective:** Defeat "The Warden" mech boss in a 3-phase tactical combat arena.
- **Boss Mechanics:**
  - **Phase 1 (Active Shield):** Deflects frontal fire; requires dodging charges and striking exposed rear thermal coils.
  - **Phase 2 (Vent Flare):** Spews tracking energy bolts and charges across the arena.
  - **Phase 3 (Overdrive):** Rapid ground slams, telegraph lines, and teleport relocations.
  - 3-hit health pip display with custom audio impact and hit flashes.

### 🔹 Level 3: Nightmare Phase (Survive Mommy)
- **Objective:** Survive for **60 seconds** in the dark house, then extract through the main entrance.
- **The Blind Mommy AI:**
  - **Blind by Design:** Mommy cannot see you across rooms. She patrols the house blindly along an autonomous room-to-room navigation DAG.
  - **Acoustic / Mic Tracking:** Real-time microphone capture detects player voice/sounds ($>3\%$ meter). If noise is made, Mommy sprints fast ($135\text{ px/s}$) through horizontal and vertical doorways straight to the sound origin.
  - **Hide & Evade:** If you hide in the Fridge, Sofa, Laundry, or Wardrobe, Mommy searches the room for **3–4 seconds**, finds nothing, resets alert, and leaves the room to continue her patrol.
  - **Glass Doors & Creaks:** Sprinting across floorboards or breaking glass doors triggers acoustic shockwaves that Mommy immediately investigates.

---

## 🛠️ Architecture & Tech Stack

```
D:/SHADOW HUNT GODOT GAME/
├── ShadowHunt.exe              # Native Windows GUI launcher
├── run_game.bat                # Windows command batch launcher
├── README.md                   # Project documentation & reference
├── .gitignore                  # Git repository exclusion rules
├── GodotEngine/                # Standalone Godot 4.7.2 runtime engine
└── HunterAssassinGodot/        # Godot 4 Game Project
    ├── project.godot           # Project configuration & display settings
    ├── Main.tscn               # Master scene container
    ├── scripts/
    │   ├── game.gd             # Core gameplay loop, AI state machine, rendering & audio
    │   ├── cg_math.gd          # Custom computer-graphics math (vectors, rays, circles, segments)
    │   ├── level3_revision_test.gd # Automated headless regression test suite
    │   └── mommy_voice_ai_test.gd  # Headless AI & acoustic room navigation test suite
    └── assets/                 # Custom sprites, textures, SFX, and environmental tiles
```

---

## 🧪 Automated Testing & Verification

The project includes headless automated regression suites that test AI pathfinding, door traversal, microphone thresholds, and combat mechanics without requiring a display:

```bash
# Run Mommy Room Navigation & Voice AI Test Suite:
GodotEngine/Godot_v4.7.2-stable_win64.exe --headless --path HunterAssassinGodot -s scripts/mommy_voice_ai_test.gd

# Run Full Level 3 Regression Test Suite:
GodotEngine/Godot_v4.7.2-stable_win64.exe --headless --path HunterAssassinGodot -s scripts/level3_revision_test.gd
```

---

## 📦 Pushing to Remote Repository

When you are ready to push this project to your GitHub / GitLab repository:

```bash
cd "D:\SHADOW HUNT GODOT GAME"
git init
git add .
git commit -m "Initial commit: Shadow Hunt Godot 4 game with native launcher and test suite"
git branch -M main
git remote add origin <YOUR_REMOTE_REPOSITORY_URL>
git push -u origin main
```

---

## 👥 Team & Technical Contributions

The project is developed by **Prithvi**, **Snehal**, and **Anushka**, spanning both the Godot 4 game engine implementation and the standalone custom computer graphics engine.

| Contributor | Focus Areas | Primary Systems & Deliverables (With & Without Game Engine) |
| :--- | :--- | :--- |
| **Prithvi** | Nightmare Stage Lead, Acoustic Horror AI, Master Architecture & C++ Rasterization | **With Engine:** Complete Level 3 Nightmare Stage & Voice AI System (Mommy blind navigation DAG, live microphone bus decibel analysis, floor/glass acoustic shockwaves, Level 3 hiding/search mechanics, 60s survival countdown), Master Game Loop & Engine Coordinator (`game.gd`), Player Kinematics & Sprint Physics, Headless Automated Test Suites (`mommy_voice_ai_test.gd`, `level3_revision_test.gd`), Native Launcher (`ShadowHunt.exe`, `run_game.bat`).<br>**Without Engine:** Phase 1 C++ Rasterization Engine (Bresenham line, Midpoint circle/ellipse, custom framebuffer & PPM export), Phase 3 Homogeneous 2D TSR matrix transformation pipeline, Phase 5 Mathematical line & polygon clipping kernels (Cohen-Sutherland, Liang-Barsky, Sutherland-Hodgman). |
| **Snehal** | Warden Boss Battle Combat Engine, Stealth AI & Dynamic FOV, 2D Math & Visualizers | **With Engine:** Level 2 Complete Warden Boss Combat Engine (3-phase state machine: directional shield reflection, homing spread-shots, overdrive teleport & ground slams, hit pips & combat feel), 90° Dynamic Raycast Field-of-View (FOV) cone & line-of-sight generation, Patrol Guards & Shielded Enforcer combat mechanics, Flank detection, Computational geometry library (`cg_math.gd`), Hiding spots & stealth dampening.<br>**Without Engine:** Phase 2 C++ & Python 2D transformation math engine ($3\times 3$ matrices, entity hierarchies, pivot kinematics), Autonomous entity state machines & security cameras, Phase 5 Interactive Line & Polygon Clipping GUI Visualizer tool. |
| **Anushka** | Graphics Algorithms, UI/UX Systems, Audio Synthesis & Visualizers | **With Engine:** Dynamic HUD overlay, Real-time microphone decibel audio meter, Stealth alert state indicators, Level 1 tactical compound architecture & tilemaps, Programmatic procedural audio synthesis (lasers, klaxons, clangs), Particle effect triggers, Pause & mission navigation menus.<br>**Without Engine:** Phase 4 Polygon Area Filling Engine (4/8-connected Boundary Fill, recursive/iterative Flood Fill, Scan-Line Polygon Fill with Edge Table & Active Edge Table), Phase 4 Real-time interactive filling visualizer GUI, Phase 2 & 3 Collectibles & score engine, Phase 5 Level Catalog & asset management. |

> 📖 **Full Specification:** For in-depth technical breakdowns and algorithm descriptions, refer to [**`CONTRIBUTIONS.md`**](file:///D:/SHADOW%20HUNT%20GODOT%20GAME/CONTRIBUTIONS.md).

---

## 📄 License & Credits
- **Engine:** Godot Engine 4.7.2 (MIT License).
- **Audio & Assets:** Custom generated synthesized audio tones, CC0 textures, and ported game art assets.
- **Authors:** Prithvi, Snehal, Anushka.

