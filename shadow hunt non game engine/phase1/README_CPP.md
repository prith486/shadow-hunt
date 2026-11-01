# Hunter Assassin - Phase 1 (C++ Port)

## 1. Overview
This is the complete C++ port of the **Hunter Assassin Phase 1** Python codebase (`graphics.py`, `map.py`, `main.py`).

The core computer graphics algorithms are preserved with **100% mathematical fidelity**:
1. **DDA Line Drawing Algorithm** (`assign1.cpp` / `graphics.py` port)
2. **Bresenham's Line Drawing Algorithm** (`assign1b.cpp` / `graphics.py` port, generalized for all 8 octants with $P = 2\Delta y - \Delta x$ decision parameter updates)

---

## 2. File Organization
| File | Python Source | Description |
| :--- | :--- | :--- |
| `core_graphics.h` | `graphics.py` | Algorithm declarations for `drawLineDDA` and `drawBresenhamLine` with camera viewport support. |
| `core_graphics.cpp` | `graphics.py` / `assign1.cpp` / `assign1b.cpp` | Exact implementations of DDA (floating point increments) and Bresenham (integer decision parameter). |
| `game_map.h` | `map.py` | Map constants ($20 \times 36$ grid, $50\text{px}$ cells, $1800 \times 1000\text{px}$ world), `Rect`, `WallSegment`, and `GameMap` declarations. |
| `game_map.cpp` | `map.py` | Procedural generation (BFS zero-object grouping for wooden crates and peach blocks, wall boundaries) and drawing routines. |
| `main.cpp` | `main.py` | WinBGIm window initialization ($900 \times 600$), zero-flicker double buffering, camera clamping, HUD, and 60 FPS game loop. |
| `compile_and_run.bat` | N/A | One-click build and execution script for MinGW GCC. |
| `hunter_assassin_phase1.exe` | N/A | Pre-built standalone executable. |

---

## 3. Algorithm Mapping to Visual Elements
- **Walls (Thickness = 5px):** Drawn using **Bresenham's Algorithm** with an offset from -2 to +2.
- **Wooden Crates ($50 \times 50\text{px}$):** Wireframe bounding box and internal diagonal cross (`X`) drawn using **Bresenham's Algorithm**.
- **Peach Blocks ($50 \times 50\text{px}$):** Wireframe bounding box and internal crosshairs (`+`) drawn using the **DDA Algorithm**.
- **Debug Grid:**
  - Vertical lines: **Bresenham's Algorithm**.
  - Horizontal lines: **DDA Algorithm**.
- **Character Outline:**
  - Triangular body: **Bresenham's Algorithm**.
  - Weapon crosshair: **DDA Algorithm**.

---

## 4. How to Compile & Run

### Option A: One-Click Runner
Double-click:
```bat
compile_and_run.bat
```

### Option B: Manual Command Line
```powershell
g++ -c core_graphics.cpp -o core_graphics.o
g++ -c game_map.cpp -o game_map.o
g++ -c main.cpp -o main.o
g++ core_graphics.o game_map.o main.o -lbgi -lgdi32 -lcomdlg32 -luuid -loleaut32 -lole32 -o hunter_assassin_phase1.exe
./hunter_assassin_phase1.exe
```

---

## 5. Controls
- **Arrow Keys / W, A, S, D:** Pan camera smoothly across the $1800 \times 1000\text{px}$ game world
- **[G]:** Toggle Debug Grid ON/OFF
- **[R]:** Reset camera to $(0, 0)$
- **[ESC] / [Q]:** Exit cleanly
