# Hunter Assassin - Phase 4 (Live Polygon Filling Implementation)

## 1. Overview
In **Phase 4**, the core Computer Graphics Assignment 4 algorithms are implemented and rendered live on screen:
- **4-Connected Boundary Fill Algorithm** (`boundaryFill4` / `boundary_fill_from`)
- **Bresenham's Line Algorithm** (Polygon boundary generation)
- **Even-Odd Parity Test** (`is_inside_polygon` for interior seed point verification)

---

## 2. All Colored Entities Supported in Live Fill Engine
You can inspect and demonstrate the live boundary fill for **EVERY colored object** in the game, in their **exact colors, vertices, and live changing coordinates**:

| Entity | Shape | Boundary Color | Fill Color | Selection |
| :--- | :--- | :--- | :--- | :--- |
| **Player Operative** | 4-point Chevron Triangle | Emerald `#34d399` | Green `#10b981` | Button / Key `[1]` / Click Player |
| **Patrol Guard** | 4-point Triangle | Red `#f87171` | Red `#ef4444` | Button / Key `[2]` / Click Guard |
| **Shielded Enforcer** | 4-point Triangle + Arc | Cyan `#00e5ff` | Dark Red `#dc2626` | Button / Key `[3]` / Click Shielded |
| **Enemy Vision Cone** | Angular Sweeping Arc Wedge | Amber `#f59e0b` | Orange `#d97706` | Button / Key `[4]` / Click Cone |
| **Security Camera Cone**| Corner Sweeping Arc Wedge | Cyan `#06b6d4` | Dark Cyan `#0891b2`| Button / Key `[5]` / Click Cam Cone |
| **Collectible Coin** | 16-Sided Circle Polygon | Gold `#facc15` | Yellow `#eab308` | Button / Key `[6]` / Click Coin |
| **Health Kit** | 12-Sided Cross Plus Symbol | White `#ffffff` | Medical Red `#ef4444`| Button / Key `[7]` / Click MedKit |
| **Exit Door Pad** | Rectangular Extraction Pad | Mint `#22c55e` | Emerald `#059669` | Button / Key `[8]` / Click Exit Door |

---

## 3. How to Demonstrate in Viva / Presentation

1. **Click-to-Inspect**:
   - Simply **click on ANY colored object on the game canvas** (Player, Guard, Cone, Coin, MedKit, Exit Door).
   - The panel immediately switches to that entity, displaying its exact vertices, boundary color, fill color, and interior seed point!

2. **Live Coordinate Tracking**:
   - Move the player with **W, A, S, D** $\rightarrow$ watch the coordinates update in real time while the boundary fill maintains the shape!
   - As enemies patrol or cameras sweep $\rightarrow$ their vision cone coordinates and fill dynamically update!

3. **Step-by-Step Slow-Mo Demonstration (`[F]` key)**:
   - Press **`[F]`** (or click the **"Slow-Mo Fill Animation [F]"** button).
   - The visualizer animates the 4-connected boundary fill algorithm spreading outward from the seed point pixel-by-pixel right before the evaluator!

---

## 4. How to Run
Double-click:
```bat
run_phase4.bat
```
Or execute:
```powershell
py main.py
```

---

## 5. Controls
| Key / Action | Function |
| :--- | :--- |
| **W, A, S, D / Arrow Keys** | Move Operative (coordinates update live) |
| **Click on ANY Object** | Inspect that object's boundary fill in the panel |
| **[1] to [8] / [TAB]** | Switch between all 8 colored entity targets |
| **[F]** | Trigger Slow-Mo Step-by-Step Boundary Fill Demo |
| **[H]** | Toggle Midpoint Circle Hitbox |
| **[R]** | Restart Game |
