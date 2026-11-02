# Project Architecture & Team Contributions

**Project:** Shadow Hunt — Stealth Tactical Assassin & Computer Graphics Simulation  
**Repository:** [https://github.com/prith486/shadow-hunt](https://github.com/prith486/shadow-hunt)  
**Authors:** Prithvi, Snehal, Anushka  

---

## Executive Summary

The **Shadow Hunt** project spans two complementary engineering systems:
1. **With Game Engine (Godot 4 Engine — GDScript & C4/2D Architecture):** A complete 2D tactical stealth action game featuring dynamic raycasted fields of view, multi-phase boss mechanics, acoustic horror AI with live microphone tracking, and automated headless test suites.
2. **Without Game Engine (Custom Computer Graphics Engine — C++ & Python):** A modular, from-scratch software rasterization and graphics mathematics pipeline spanning five major academic and practical phases: Bresenham line/circle/ellipse drawing, homogeneous 2D transformation matrix stacks, TSR animation pipelines, polygon area filling (Boundary, Flood, Scan-Line ET/AET), and 2D clipping algorithms (Cohen-Sutherland, Liang-Barsky, Sutherland-Hodgman) with live interactive visualization tools.

---

## Comprehensive Contribution Matrix

| Functional Area | Subsystem / Module | Primary Lead | Key Deliverables & Algorithms |
| :--- | :--- | :--- | :--- |
| **With Engine (Godot 4)** | Master Game Loop & State Machine | **Prithvi** | `game.gd` master coordinator, phase lifecycle, session state, frame-delta synchronization |
| **With Engine (Godot 4)** | Level 2: Warden Boss Multi-Phase System | **Prithvi** | 3-phase state machine: directional shield reflection, homing spread-shots, overdrive teleport & ground slams |
| **With Engine (Godot 4)** | Level 3: Acoustic Horror AI & Mic Input | **Prithvi** | Real-time audio bus capture, decibel threshold normalization, acoustic alert propagation to room nodes |
| **With Engine (Godot 4)** | Headless CI & Regression Test Suites | **Prithvi** | `mommy_voice_ai_test.gd`, `level3_revision_test.gd` (zero-display automated verification) |
| **With Engine (Godot 4)** | Native Packaging & Launcher Scripts | **Prithvi** | Windows native binary packaging (`ShadowHunt.exe`), orchestrator scripts (`run_game.bat`) |
| **With Engine (Godot 4)** | Stealth AI & Dynamic FOV Raycasting | **Snehal** | 90° FOV cone mathematical projections, ray-march obstacle occlusion, LOS visibility polygon calculation |
| **With Engine (Godot 4)** | Enemy Archetypes & Combat Mechanics | **Snehal** | Waypoint patrol guards, enforcer riot-shield deflection physics, flank detection, instant takedown logic |
| **With Engine (Godot 4)** | Computational Geometry Math Library | **Snehal** | `cg_math.gd` (ray-plane intersections, circle-box sweep tests, capsule segment projections) |
| **With Engine (Godot 4)** | Tactical Concealment & Stealth Interactivity | **Snehal** | Hiding spots (Wardrobes, Fridge, Sofa, Laundry), stealth sneaking footstep dampening, quiet glass doors |
| **With Engine (Godot 4)** | Dynamic HUD & Player Status Overlays | **Anushka** | Dynamic health pips, real-time mic decibel level meter, detection status indicators, contextual input prompts |
| **With Engine (Godot 4)** | Level 1 Compound Layout & Tile Architecture | **Anushka** | Tactical compound design, camera placements, obstacle corridors, extraction gate trigger zones |
| **With Engine (Godot 4)** | Programmatic Audio Synthesis & Visual FX | **Anushka** | Real-time tone synthesis (lasers, klaxons, shield clangs), particle emitters (sparks, charge trails, flash) |
| **With Engine (Godot 4)** | Pause Menu & Level Navigation System | **Anushka** | Pause menu dialogs, level selection interfaces, input re-mapping overlay, restart/quit controls |
| **Without Engine (CG Pipeline)** | Phase 1: Core C++ Rasterization Engine | **Prithvi** | Bresenham's Integer Line Drawing, Midpoint Circle, Midpoint Ellipse, custom frame buffer, PPM exporter |
| **Without Engine (CG Pipeline)** | Phase 3: Composite 2D Transformation Pipeline | **Prithvi** | Homogeneous 2D matrix transformation stack, Translate-Scale-Rotate compositor, scene graph hierarchy |
| **Without Engine (CG Pipeline)** | Phase 5: Mathematical Clipping Kernels | **Prithvi** | Cohen-Sutherland (4-bit outcodes), Liang-Barsky parametric line clipping ($u_1, u_2$), Sutherland-Hodgman polygon clipping |
| **Without Engine (CG Pipeline)** | Phase 2: C++ & Python 2D Math Engine | **Snehal** | Homogeneous $3\times 3$ matrix multiplication, local-to-world transformations, pivot rotation, entity bounding boxes |
| **Without Engine (CG Pipeline)** | Phase 2 & 3: Autonomous Entity Simulation | **Snehal** | Custom patrol pathing, sweeping security camera angular arcs, detection state machines without game physics |
| **Without Engine (CG Pipeline)** | Phase 5: Interactive Clipping Visualizer Tool | **Snehal** | Real-time GUI visualizer demonstrating live outcode evaluation, parametric clipping, and polygon vertex clipping |
| **Without Engine (CG Pipeline)** | Phase 4: Polygon Area Filling Engine | **Anushka** | Boundary Fill (4/8-connected), Flood Fill (recursive/iterative), Scan-Line Polygon Fill with Edge Table (ET) & AET |
| **Without Engine (CG Pipeline)** | Phase 4: Real-Time Filling Visualizer | **Anushka** | `live_fill_visualizer.py` interactive GUI displaying scanline progress, active edge updates, and pixel fill steps |
| **Without Engine (CG Pipeline)** | Phase 2 & 3: Collectibles & Scoring Mechanics | **Anushka** | Keycard and coin distribution, proximity pickups, score counters, HUD text overlay without game engine UI |
| **Without Engine (CG Pipeline)** | Phase 5: Level Catalog & Asset Management | **Anushka** | Multi-level parser, procedural tilemap loader, asset catalog structure, grid-to-world coordinate mapping |

---

## Detailed Individual Contributions

### 1. Prithvi
*Role: Core Engine Architect, Systems Programmer & Advanced Algorithms Lead*

#### With Game Engine (Godot 4):
- **Master Gameplay Coordinator (`scripts/game.gd`):** Architected the core game loop, lifecycle manager, scene transitions, delta-time smoothing, and global game state machine.
- **The Warden Boss Encounter (Level 2 Multi-Phase Combat):**
  - Designed the 3-phase combat state machine for the Warden mech.
  - Phase 1: Frontal kinetic shield deflection algorithm utilizing normal vector reflections and rear vulnerability strike zones.
  - Phase 2: Multi-directional spread projectile bursts with predictive angular steering.
  - Phase 3: Overdrive berserk phase featuring teleport relocations, telegraph warning rays, and radial ground slam shockwaves.
  - Hit pip health system with custom audio impact signals and frame-freeze combat feel.
- **Acoustic Horror Subsystem & Voice AI (Level 3 Nightmare):**
  - Integrated Godot's audio bus capture to poll live microphone decibel amplitude.
  - Engineered acoustic wave alert propagation that informs the blind Mommy AI's navigation graph.
  - Authored the autonomous room-to-room navigation DAG allowing Mommy to patrol blindly and investigate audio disturbances dynamically.
- **Headless Automated Test Infrastructure:**
  - Built `scripts/level3_revision_test.gd` and `scripts/mommy_voice_ai_test.gd` running headlessly via Godot CLI.
  - Automated verification of room navigation DAGs, sound trigger thresholds, collision boxes, and takedown mechanics.
- **Native Deployment Pipeline:**
  - Packaged standalone Windows binary (`ShadowHunt.exe`) and batch runtime orchestrators (`run_game.bat`).

#### Without Game Engine (Computer Graphics C++ & Python Pipeline):
- **Phase 1: High-Performance C++ Rasterization Engine (`phase1/assignment1_algorithms.cpp`, `core_graphics.cpp`):**
  - Implemented Bresenham's Integer Line Drawing algorithm for all octants avoiding floating-point division.
  - Implemented Midpoint Circle and Midpoint Ellipse Drawing algorithms with full mathematical derivation of initial decision parameters ($p_0$, $p_{10}$, $p_{20}$).
  - Built custom frame buffer abstraction and binary PPM image file exporter.
- **Phase 3: 2D Composite Transformation & TSR Pipeline (`phase3/transforms.py`, `phase3/main_tsr.py`):**
  - Formulated the homogeneous coordinate matrix pipeline using $3\times 3$ affine transformation matrices.
  - Engineered the Translate-Scale-Rotate (TSR) pipeline supporting arbitrary fixed-point rotation and scaling.
  - Implemented hierarchical scene graph traversal for multi-part rendering.
- **Phase 5: Advanced 2D Line and Polygon Clipping Kernels (`phase5/cg_math.py`, `phase5/main_clipping.py`):**
  - Implemented Cohen-Sutherland line clipping with 4-bit region outcodes (Top, Bottom, Right, Left) and trivial accept/reject bitwise masks.
  - Implemented Liang-Barsky parametric line clipping using direction vectors and parameter intervals $[u_1, u_2]$.
  - Implemented Sutherland-Hodgman polygon clipping against arbitrary rectangular clipping windows, outputting trimmed vertex lists.

---

### 2. Snehal
*Role: Lead Graphics Engineer, AI Logic & Combat Mechanics Specialist*

#### With Game Engine (Godot 4):
- **Dynamic Field of View (FOV) & Raycasting Vision System:**
  - Engineered the 2D vision cone algorithm with $90^\circ$ FOV sweeps and heading dot-product calculations.
  - Implemented continuous ray-marching against wall and crate geometry to cast dynamic shadows and generate line-of-sight (LOS) vision polygons.
- **Enemy Archetypes & Combat Logic:**
  - Developed the **Patrol Guard** behavior tree: cyclic waypoint pathing, vision detection buildup (Unaware $\to$ Suspicious $\to$ Alert), and high-velocity laser projectile fire.
  - Designed the **Enforcer (Shielded Guard)** archetype: forward riot shield blocking all frontal takedowns and ranged attacks, requiring player flanking and rear takedowns.
  - Authored instant melee takedowns from behind with angle checks and audio feedback.
- **Computational Geometry & Collision Utility (`scripts/cg_math.gd`):**
  - Authored mathematical helper modules for ray-box intersections, circle-box sweep tests, capsule segment projections, and line-to-line intersection queries.
- **Stealth Concealment & Environmental Interactions:**
  - Implemented interactive hiding spot logic (Wardrobes, Refrigerators, Sofas, Laundry Baskets) that break enemy pursuit sightlines and reset enemy alert timers.
  - Implemented sneak walk mechanics (`E` key) reducing footstep acoustic radius, and quiet glass door opening mechanics.

#### Without Game Engine (Computer Graphics C++ & Python Pipeline):
- **Phase 2: 2D Matrix Mathematics & Entity Architecture (`phase2/cg_math.cpp`, `entities.cpp`, `map_engine.cpp`):**
  - Designed the C++ and Python 2D transformation math engine: homogeneous $3\times 3$ matrix operations, forward kinematics for entity pivots, and bounding box transformations.
  - Developed the object-oriented entity model in C++ (`Player`, `Enemy`, `Obstacle`, `MapEngine`).
- **Phase 2 & Phase 3: Autonomous Entity Simulation & Security Cameras (`phase2/enemy.py`, `phase3/enemy.py`, `security_camera.py`):**
  - Programmed autonomous patrol algorithms and sweeping security camera angular arcs without relying on built-in physics engines.
  - Implemented mathematical line-of-sight checks against rasterized grid tiles.
- **Phase 5: Interactive Clipping Visualizer Tool (`phase5/clipping_visualizer.py`, `live_clipping_visualizer.py`):**
  - Developed the live interactive GUI visualizer demonstrating Cohen-Sutherland outcode evaluations, Liang-Barsky intersection updates, and live polygon vertex clipping against dynamic clip windows.
  - Provided interactive mouse controls to reposition lines, resize clipping rectangles, and observe algorithm execution steps.

---

### 3. Anushka
*Role: Graphics Algorithms Specialist, UI/UX Designer & Systems Integration Lead*

#### With Game Engine (Godot 4):
- **Dynamic In-Game HUD & User Interface:**
  - Engineered the tactical HUD overlay displaying remaining player health pips, objective notifications, and mission timers.
  - Developed the live real-time microphone decibel meter with animated noise threshold bars for the Level 3 Nightmare stage.
  - Implemented dynamic state indicator icons (Undetected, Suspicious, Alerted, Hidden in Wardrobe/Fridge/Sofa/Laundry) and contextual action tooltips.
- **Level 1 Facility Architecture & Level Design:**
  - Constructed the spatial layout for Level 1 (The Compound), including patrol paths, concealment alcoves, security camera coverage zones, and extraction gate extraction zones.
- **Audio Synthesis & Visual FX Systems:**
  - Integrated real-time programmatic audio synthesis generating laser discharge tones, alarm sirens, shield deflection clangs, and footstep sound effects.
  - Implemented visual particle emitters for laser impacts, takedown flashes, boss charge smoke trails, and hit sparks.
- **Pause System & Mission Navigation:**
  - Created the pause menu interface, mission restart triggers, controls reference screen, and level selection menus.

#### Without Game Engine (Computer Graphics C++ & Python Pipeline):
- **Phase 4: Polygon Area Filling Engine (`phase4/fill_algo.py`):**
  - Implemented 4-Connected and 8-Connected Boundary Fill algorithms with boundary color checking.
  - Implemented recursive and iterative Flood Fill algorithms with replacement color criteria.
  - Researched and developed the Scan-Line Polygon Fill algorithm utilizing Edge Table (ET) and Active Edge Table (AET) sorted by $y_{\min}$, tracking $x$-intersections and inverse slopes ($1/m$).
- **Phase 4: Real-Time Filling Visualizer (`phase4/live_fill_visualizer.py`):**
  - Built the interactive GUI visualizer demonstrating animated scanline sweeps across complex polygons.
  - Implemented live visualization of parity checking, edge intersection points, and rasterized pixel span filling.
- **Phase 2 & Phase 3: Collectibles & Scoring Mechanics (`phase2/collectibles.py`, `phase3/collectibles.py`):**
  - Designed collectible keycard and coin placement algorithms, collision pick-up triggers, score tallying, and HUD text rendering on raw framebuffers.
- **Phase 5: Level Catalog & Asset Management (`phase5/level_catalog.py`):**
  - Designed the multi-level configuration parser, procedural tilemap loader, asset catalog structure, and coordinate mapping between grid space and world coordinate space.

---

## Verification & Build Integrity

All components across both systems are fully verified and reproducible:
- **Godot Game Automated Regression:** Headless verification via `scripts/level3_revision_test.gd` and `scripts/mommy_voice_ai_test.gd` passes with 0 errors.
- **Non-Engine Graphics Suite:** All batch scripts (`compile_and_run.bat`, `run_phase4.bat`, `run_phase5.bat`, `run_clipping.bat`) compile cleanly and run interactive visualizers out-of-the-box.
