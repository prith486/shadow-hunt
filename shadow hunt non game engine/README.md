# Shadow Hunt — Standalone Computer Graphics Engine & Algorithm Suite

A modular, from-scratch 2D computer graphics and algorithm implementation built in C++ and Python, demonstrating fundamental computational geometry, software rasterization, 2D transformations, area filling, and clipping.

---

## 📚 Curriculum & Phase Breakdown

| Phase | Module | Language | Key Algorithms & Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **Software Rasterization Engine** | C++ / Python | Bresenham's Integer Line Drawing (all octants), Midpoint Circle Drawing Algorithm, Midpoint Ellipse Drawing Algorithm, custom raw frame buffer, and binary PPM image exporter. |
| **Phase 2** | **2D Math & Entity Simulation** | C++ / Python | $3\times 3$ Homogeneous transformation matrices, forward kinematics for entity pivots, local-to-world coordinate transformations, autonomous patrol enemies, and sweeping security camera FOV. |
| **Phase 3** | **Composite Transformations & TSR** | Python (Pygame) | Composite 2D transformation pipelines (Translate-Scale-Rotate compositor), arbitrary fixed-point rotation, hierarchical scene graphs, dynamic camera viewport tracking, and collectibles. |
| **Phase 4** | **Polygon Area Filling Suite** | Python (Tkinter/Pygame) | 4-Connected and 8-Connected Boundary Fill, recursive/iterative Flood Fill, Scan-Line Polygon Fill with Edge Table (ET) & Active Edge Table (AET), plus interactive live filling visualizer. |
| **Phase 5** | **Line & Polygon Clipping Suite** | Python (Tkinter/Pygame) | Cohen-Sutherland line clipping (4-bit region outcodes), Liang-Barsky parametric line clipping ($[u_1, u_2]$ intervals), Sutherland-Hodgman polygon clipping, level catalog loader, and real-time interactive clipping visualizer GUI. |

---

## 👥 Module Ownership & Contributions

This non-game engine suite was designed and implemented by **Prithvi**, **Snehal**, and **Anushka**:

- **Prithvi:** Phase 1 Core C++ Rasterization Engine (`assignment1_algorithms.cpp`, `core_graphics.cpp`), Phase 3 Homogeneous 2D TSR transformation matrix pipeline (`transforms.py`, `main_tsr.py`), Phase 5 Mathematical line & polygon clipping kernels (`cg_math.py`, `main_clipping.py`).
- **Snehal:** Phase 2 C++ & Python 2D transformation math engine (`cg_math.cpp`, `entities.cpp`, `map_engine.cpp`), Phase 2 & 3 Autonomous entity simulation & security camera arcs (`enemy.py`, `security_camera.py`), Phase 5 Interactive line & polygon clipping GUI visualizer tool (`clipping_visualizer.py`, `live_clipping_visualizer.py`).
- **Anushka:** Phase 4 Polygon Area Filling Engine (`fill_algo.py` — Boundary, Flood, and Scan-Line with ET/AET), Phase 4 Real-time interactive scanline filling visualizer GUI (`live_fill_visualizer.py`), Phase 2 & 3 Collectibles and score engine (`collectibles.py`), Phase 5 Level Catalog and multi-level asset management (`level_catalog.py`).

> 📖 **Full Project Breakdown:** See the root [**`CONTRIBUTIONS.md`**](../CONTRIBUTIONS.md) for full system attribution including the Godot 4 game engine implementation.

---

## 🚀 How to Run the Visualizers

### Phase 1 (C++ Primitives):
```cmd
cd phase1
compile_and_run.bat
```

### Phase 4 (Polygon Fill Visualizer):
```cmd
cd phase4
run_phase4.bat
```

### Phase 5 (Interactive Clipping Visualizer & Game Prototype):
```cmd
cd phase5
run_clipping.bat
# or
run_phase5.bat
```
