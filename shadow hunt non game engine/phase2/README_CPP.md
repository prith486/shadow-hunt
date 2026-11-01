# Hunter Assassin - Phase 2 (C++ Port)

## 1. Overview
This is the complete C++ port of the **Hunter Assassin Phase 2** Python codebase (`graphics.py`, `cg_math.py`, `player.py`, `enemy.py`, `security_camera.py`, `collectibles.py`, `map_engine.py`, `main.py`).

The core computer graphics algorithms are preserved with **100% mathematical fidelity**:
1. **DDA Line Drawing Algorithm** (`assign1.cpp`)
2. **Bresenham's Line Drawing Algorithm** (`assign1b.cpp` - all octants)
3. **Midpoint Circle Algorithm** (`assign2.cpp` - decision parameter $del = 2 \times (1 - r)$ with 8-way symmetry)
4. **Homogeneous 3x3 Affine Transformation Matrices** (`assign3 (1).cpp` - Translation, Rotation, Scaling composite matrices)
5. **Ray-Casting Point-in-Polygon Algorithm** (Vision cones for security cameras and enemy FOV sweeps)

> **Important Note:** As requested, **all intermediate debug grid lines have been removed**, producing a clean wireframe map environment with walls, crates, sliding doors, and exit zones.

---

## 2. File Organization
| File | Python Source | Description |
| :--- | :--- | :--- |
| `core_graphics.h` / `core_graphics.cpp` | `graphics.py` | Standalone ports of `assign1.cpp` (DDA), `assign1b.cpp` (Bresenham), and `assign2.cpp` (Midpoint Circle). |
| `cg_math.h` / `cg_math.cpp` | `cg_math.py` | 3x3 Transformation Matrices (Translation, Rotation, Scaling composite matrices), distance, ray-casting point-in-polygon, and cone polygon generation. |
| `map_engine.h` / `map_engine.cpp` | `map_engine.py` | Parametric facility layout: outer walls, 6 crossed crates, 3 sliding doors, and glowing exit door. **Grid lines omitted**. |
| `entities.h` / `entities.cpp` | `player.py`, `enemy.py`, `security_camera.py`, `collectibles.py` | Assassin operative, Guard & Shielded Enforcers, Security Camera with FOV sweep cone, Coins & Health Kits. |
| `main.cpp` | `main.py` | WinBGIm window initialization ($980 \times 820$), header HUD banner, zero-flicker double buffering, and 60 FPS loop. |
| `compile_and_run.bat` | N/A | One-click compilation and execution script for MinGW GCC. |
| `hunter_assassin_phase2.exe` | N/A | Pre-built standalone executable. |

---

## 3. How to Compile & Run

### Option A: One-Click Runner
Double-click:
```bat
compile_and_run.bat
```

### Option B: Manual Command Line
```powershell
g++ -c core_graphics.cpp -o core_graphics.o
g++ -c cg_math.cpp -o cg_math.o
g++ -c map_engine.cpp -o map_engine.o
g++ -c entities.cpp -o entities.o
g++ -c main.cpp -o main.o
g++ core_graphics.o cg_math.o map_engine.o entities.o main.o -lbgi -lgdi32 -lcomdlg32 -luuid -loleaut32 -lole32 -o hunter_assassin_phase2.exe
./hunter_assassin_phase2.exe
```

---

## 4. Controls
- **[H]:** Toggle Midpoint Circle Hitbox rendering for operative and enemies
- **[R]:** Restart and reset the simulation
- **[ESC] / [Q]:** Exit cleanly
