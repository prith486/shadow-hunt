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

## 📄 License & Credits
- **Engine:** Godot Engine 4.7.2 (MIT License).
- **Audio & Assets:** Custom generated synthesized audio tones, CC0 textures, and ported game art assets.

