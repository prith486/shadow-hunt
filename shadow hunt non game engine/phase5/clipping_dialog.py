"""
Phase 5 — Standalone Tkinter User Input & Clipping Dialog
=========================================================
Allows users to directly input polygon type, custom vertices, clipping method,
and viewport bounds using a Tkinter GUI.
Computes and visualizes clipping results using Phase 5 core algorithms from cg_math.py:
- Sutherland-Hodgman Polygon Clipping (CGMath.clip_polygon_aabb)
- Cohen-Sutherland Line Clipping (CGMath.clip_line_cohen_sutherland)
- 4-bit Outcodes (CGMath.get_code)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import math
from typing import List, Tuple, Optional

# Ensure phase5 is in sys.path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from cg_math import CGMath

Point = Tuple[float, float]
Points = List[Point]

PRESET_POLYGONS = {
    "Triangle (Crossing)": [(140.0, 130.0), (460.0, 170.0), (290.0, 470.0)],
    "Convex Pentagon": [(280.0, 110.0), (500.0, 210.0), (440.0, 460.0), (150.0, 430.0), (120.0, 230.0)],
    "Concave Star (10 Vertices)": [
        (300.0, 90.0), (345.0, 210.0), (470.0, 210.0), (370.0, 280.0),
        (410.0, 410.0), (300.0, 330.0), (190.0, 410.0), (230.0, 280.0),
        (130.0, 210.0), (255.0, 210.0)
    ],
    "Vision Cone (Assassin)": [
        (120.0, 280.0), (480.0, 140.0), (510.0, 210.0),
        (520.0, 280.0), (510.0, 350.0), (480.0, 420.0)
    ],
    "Arrow / Dart": [
        (140.0, 230.0), (360.0, 120.0), (360.0, 200.0), (480.0, 200.0),
        (480.0, 260.0), (360.0, 260.0), (360.0, 340.0)
    ],
    "Custom User Input": []
}


class ClippingDialogApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Phase 5 — Polygon & Line Clipping User Input Suite")
        self.root.geometry("1060x720")
        self.root.configure(bg="#070a12")

        # Top Title Header
        header = tk.Frame(root, bg="#0d131f", height=50)
        header.pack(fill=tk.X, side=tk.TOP)

        title_lbl = tk.Label(
            header,
            text="PHASE 5: POLYGON & LINE CLIPPING ENGINE",
            font=("Consolas", 14, "bold"),
            fg="#22c55e",
            bg="#0d131f"
        )
        title_lbl.pack(side=tk.LEFT, padx=16, pady=10)

        launch_pygame_btn = tk.Button(
            header,
            text="🚀 Open 60FPS Interactive Visualizer",
            font=("Consolas", 10, "bold"),
            fg="#070a12",
            bg="#38bdf8",
            activebackground="#0284c7",
            padx=12,
            pady=3,
            relief=tk.FLAT,
            command=self.launch_interactive_pygame
        )
        launch_pygame_btn.pack(side=tk.RIGHT, padx=16, pady=8)

        # Main Layout: Left Control Panel + Right Canvas Preview
        main_frame = tk.Frame(root, bg="#070a12")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Control Panel
        ctrl_frame = tk.LabelFrame(
            main_frame,
            text=" [ USER INPUT CONFIGURATION ] ",
            font=("Consolas", 11, "bold"),
            fg="#facc15",
            bg="#0d131f",
            padx=12,
            pady=10,
            width=380
        )
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        ctrl_frame.pack_propagate(False)

        # 1. Polygon Type Selection
        tk.Label(ctrl_frame, text="1. Select Polygon Type:", font=("Consolas", 10, "bold"), fg="#e2e8f0", bg="#0d131f").pack(anchor=tk.W, pady=(4, 2))
        self.poly_choice_var = tk.StringVar(value="Triangle (Crossing)")
        self.poly_combo = ttk.Combobox(ctrl_frame, textvariable=self.poly_choice_var, values=list(PRESET_POLYGONS.keys()), state="readonly")
        self.poly_combo.pack(fill=tk.X, pady=(0, 8))
        self.poly_combo.bind("<<ComboboxSelected>>", self.on_poly_selected)

        # Custom coordinates box
        tk.Label(ctrl_frame, text="Vertices (x1 y1, x2 y2, ...):", font=("Consolas", 9), fg="#94a3b8", bg="#0d131f").pack(anchor=tk.W)
        self.custom_coords_text = tk.Text(ctrl_frame, height=3, font=("Consolas", 9), bg="#050811", fg="#38bdf8", insertbackground="white", relief=tk.SOLID, borderwidth=1)
        self.custom_coords_text.pack(fill=tk.X, pady=(2, 10))
        self.load_preset_coords("Triangle (Crossing)")

        # 2. Clipping Method Selection
        tk.Label(ctrl_frame, text="2. Select Clipping Method:", font=("Consolas", 10, "bold"), fg="#e2e8f0", bg="#0d131f").pack(anchor=tk.W, pady=(4, 2))
        self.method_var = tk.StringVar(value="Sutherland-Hodgman")

        m1 = tk.Radiobutton(ctrl_frame, text="Sutherland-Hodgman (Polygon Clipping)", variable=self.method_var, value="Sutherland-Hodgman", font=("Consolas", 9), fg="#22c55e", bg="#0d131f", selectcolor="#050811", activebackground="#0d131f")
        m2 = tk.Radiobutton(ctrl_frame, text="Cohen-Sutherland (Line Clipping)", variable=self.method_var, value="Cohen-Sutherland", font=("Consolas", 9), fg="#38bdf8", bg="#0d131f", selectcolor="#050811", activebackground="#0d131f")
        m3 = tk.Radiobutton(ctrl_frame, text="Dual Comparison (Both Methods)", variable=self.method_var, value="Dual Comparison", font=("Consolas", 9), fg="#facc15", bg="#0d131f", selectcolor="#050811", activebackground="#0d131f")
        m1.pack(anchor=tk.W)
        m2.pack(anchor=tk.W)
        m3.pack(anchor=tk.W, pady=(0, 10))

        # 3. Viewport Window Settings
        tk.Label(ctrl_frame, text="3. Viewport Window Bounds [xmin, ymin, xmax, ymax]:", font=("Consolas", 10, "bold"), fg="#e2e8f0", bg="#0d131f").pack(anchor=tk.W, pady=(4, 2))
        win_grid = tk.Frame(ctrl_frame, bg="#0d131f")
        win_grid.pack(fill=tk.X, pady=(0, 10))

        tk.Label(win_grid, text="Xmin:", font=("Consolas", 9), fg="#f59e0b", bg="#0d131f").grid(row=0, column=0, sticky=tk.W)
        self.xmin_ent = tk.Entry(win_grid, width=7, font=("Consolas", 9), bg="#050811", fg="white", insertbackground="white")
        self.xmin_ent.insert(0, "180")
        self.xmin_ent.grid(row=0, column=1, padx=(2, 10))

        tk.Label(win_grid, text="Ymin:", font=("Consolas", 9), fg="#f59e0b", bg="#0d131f").grid(row=0, column=2, sticky=tk.W)
        self.ymin_ent = tk.Entry(win_grid, width=7, font=("Consolas", 9), bg="#050811", fg="white", insertbackground="white")
        self.ymin_ent.insert(0, "160")
        self.ymin_ent.grid(row=0, column=3, padx=(2, 0))

        tk.Label(win_grid, text="Xmax:", font=("Consolas", 9), fg="#f59e0b", bg="#0d131f").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.xmax_ent = tk.Entry(win_grid, width=7, font=("Consolas", 9), bg="#050811", fg="white", insertbackground="white")
        self.xmax_ent.insert(0, "440")
        self.xmax_ent.grid(row=1, column=1, padx=(2, 10), pady=4)

        tk.Label(win_grid, text="Ymax:", font=("Consolas", 9), fg="#f59e0b", bg="#0d131f").grid(row=1, column=2, sticky=tk.W, pady=4)
        self.ymax_ent = tk.Entry(win_grid, width=7, font=("Consolas", 9), bg="#050811", fg="white", insertbackground="white")
        self.ymax_ent.insert(0, "390")
        self.ymax_ent.grid(row=1, column=3, padx=(2, 0), pady=4)

        # Compute & Render Button
        clip_btn = tk.Button(
            ctrl_frame,
            text="⚡ EXECUTE CLIPPING ALGORITHM",
            font=("Consolas", 11, "bold"),
            fg="#070a12",
            bg="#22c55e",
            activebackground="#16a34a",
            padx=10,
            pady=8,
            relief=tk.FLAT,
            command=self.compute_and_render
        )
        clip_btn.pack(fill=tk.X, pady=(6, 10))

        # Results & Metrics Card
        self.results_box = tk.Text(
            ctrl_frame,
            height=12,
            font=("Consolas", 9),
            bg="#050811",
            fg="#e2e8f0",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.results_box.pack(fill=tk.BOTH, expand=True)

        # Right Preview Area
        right_frame = tk.Frame(main_frame, bg="#070a12")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(right_frame, bg="#050811", highlightthickness=1, highlightbackground="#1e293b")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initial render
        self.root.after(100, self.compute_and_render)

    def load_preset_coords(self, preset_name: str):
        pts = PRESET_POLYGONS.get(preset_name, [])
        if pts:
            coords_str = ", ".join(f"{int(round(p[0]))} {int(round(p[1]))}" for p in pts)
        else:
            coords_str = "100 100, 300 100, 200 300"
        self.custom_coords_text.delete("1.0", tk.END)
        self.custom_coords_text.insert(tk.END, coords_str)

    def on_poly_selected(self, event=None):
        choice = self.poly_choice_var.get()
        self.load_preset_coords(choice)
        self.compute_and_render()

    def parse_user_inputs(self) -> Tuple[Points, float, float, float, float]:
        raw_coords = self.custom_coords_text.get("1.0", tk.END).strip().replace(";", ",").replace("\n", ",")
        tokens = raw_coords.split(",")
        pts: Points = []
        for t in tokens:
            p = t.strip().split()
            if len(p) >= 2:
                pts.append((float(p[0]), float(p[1])))

        if len(pts) < 3:
            raise ValueError("Polygon must have at least 3 vertices!")

        xmin = float(self.xmin_ent.get())
        ymin = float(self.ymin_ent.get())
        xmax = float(self.xmax_ent.get())
        ymax = float(self.ymax_ent.get())

        if xmin >= xmax or ymin >= ymax:
            raise ValueError("Invalid Viewport: xmin must be < xmax and ymin < ymax!")

        return pts, xmin, ymin, xmax, ymax

    def compute_and_render(self):
        try:
            poly, xmin, ymin, xmax, ymax = self.parse_user_inputs()
        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            return

        method = self.method_var.get()

        # Run Phase 5 Core Algorithms
        sh_clipped = CGMath.clip_polygon_aabb(poly, xmin, ymin, xmax, ymax)

        # Cohen-Sutherland line edges
        cs_edges = []
        n = len(poly)
        for i in range(n):
            p1 = poly[i]
            p2 = poly[(i + 1) % n]
            res = CGMath.clip_line_cohen_sutherland(p1[0], p1[1], p2[0], p2[1], xmin, ymin, xmax, ymax)
            c1 = CGMath.get_code(p1[0], p1[1], xmin, ymin, xmax, ymax)
            c2 = CGMath.get_code(p2[0], p2[1], xmin, ymin, xmax, ymax)
            cs_edges.append((p1, p2, res, c1, c2))

        # Update Results Text Box
        self.results_box.delete("1.0", tk.END)
        self.results_box.insert(tk.END, "=== CLIPPING RESULTS ===\n")
        self.results_box.insert(tk.END, f"Method: {method}\n")
        self.results_box.insert(tk.END, f"Window: [{int(xmin)},{int(ymin)}] -> [{int(xmax)},{int(ymax)}]\n")
        self.results_box.insert(tk.END, f"Original Vertices: {len(poly)}\n")
        self.results_box.insert(tk.END, f"S-H Clipped Vertices: {len(sh_clipped)}\n\n")

        self.results_box.insert(tk.END, "--- S-H Clipped Points ---\n")
        for i, cp in enumerate(sh_clipped):
            self.results_box.insert(tk.END, f" C{i+1}: ({cp[0]:.1f}, {cp[1]:.1f})\n")

        self.results_box.insert(tk.END, "\n--- C-S Edges & Outcodes ---\n")
        for i, (p1, p2, res, c1, c2) in enumerate(cs_edges):
            status = "ACCEPTED" if (c1 | c2) == 0 else ("REJECTED" if (c1 & c2) != 0 else "CLIPPED")
            self.results_box.insert(tk.END, f" E{i+1}: {c1:04b} -> {c2:04b} [{status}]\n")

        # Render to Tkinter Canvas
        self.canvas.delete("all")
        cw = self.canvas.winfo_width() or 640
        ch = self.canvas.winfo_height() or 600

        # Draw grid
        for gx in range(40, cw, 40):
            self.canvas.create_line(gx, 0, gx, ch, fill="#0f172a", width=1)
        for gy in range(40, ch, 40):
            self.canvas.create_line(0, gy, cw, gy, fill="#0f172a", width=1)

        # Draw Cohen-Sutherland Outcode labels in regions
        self.canvas.create_text(xmin - 40, ymin - 15, text="1001", fill="#b45309", font=("Consolas", 10, "bold"))
        self.canvas.create_text((xmin + xmax)/2, ymin - 15, text="1000 (TOP)", fill="#b45309", font=("Consolas", 10, "bold"))
        self.canvas.create_text(xmax + 40, ymin - 15, text="1010", fill="#b45309", font=("Consolas", 10, "bold"))

        self.canvas.create_text(xmin - 40, (ymin + ymax)/2, text="0001", fill="#b45309", font=("Consolas", 10, "bold"))
        self.canvas.create_text((xmin + xmax)/2, (ymin + ymax)/2, text="0000 (INSIDE)", fill="#f59e0b", font=("Consolas", 10, "bold"))
        self.canvas.create_text(xmax + 40, (ymin + ymax)/2, text="0010", fill="#b45309", font=("Consolas", 10, "bold"))

        self.canvas.create_text(xmin - 40, ymax + 15, text="0101", fill="#b45309", font=("Consolas", 10, "bold"))
        self.canvas.create_text((xmin + xmax)/2, ymax + 15, text="0100 (BOT)", fill="#b45309", font=("Consolas", 10, "bold"))
        self.canvas.create_text(xmax + 40, ymax + 15, text="0110", fill="#b45309", font=("Consolas", 10, "bold"))

        # Draw infinite boundary dashed lines
        self.canvas.create_line(xmin, 0, xmin, ch, fill="#1e293b", dash=(4, 4))
        self.canvas.create_line(xmax, 0, xmax, ch, fill="#1e293b", dash=(4, 4))
        self.canvas.create_line(0, ymin, cw, ymin, fill="#1e293b", dash=(4, 4))
        self.canvas.create_line(0, ymax, cw, ymax, fill="#1e293b", dash=(4, 4))

        # Viewport rectangle
        self.canvas.create_rectangle(xmin, ymin, xmax, ymax, outline="#f59e0b", width=2)
        self.canvas.create_text(xmin + 10, ymin + 12, text=f"({int(xmin)},{int(ymin)})", fill="#f59e0b", anchor=tk.W, font=("Consolas", 9))
        self.canvas.create_text(xmax - 10, ymax - 12, text=f"({int(xmax)},{int(ymax)})", fill="#f59e0b", anchor=tk.E, font=("Consolas", 9))

        # Original polygon outline (White / Silver dashed)
        orig_flat = [coord for pt in poly for coord in pt]
        if len(orig_flat) >= 6:
            self.canvas.create_polygon(orig_flat, fill="", outline="#94a3b8", width=1, dash=(3, 3))

            for i, (px, py) in enumerate(poly):
                self.canvas.create_oval(px - 4, py - 4, px + 4, py + 4, fill="#e2e8f0", outline="#070a12")
                self.canvas.create_text(px + 8, py - 8, text=f"P{i+1}", fill="#e2e8f0", font=("Consolas", 9, "bold"))

        # Render Clipped Shapes based on Method
        if method in ("Sutherland-Hodgman", "Dual Comparison"):
            if len(sh_clipped) >= 3:
                clip_flat = [coord for pt in sh_clipped for coord in pt]
                # Filled polygon
                self.canvas.create_polygon(clip_flat, fill="#15803d", stipple="gray25", outline="#22c55e", width=3)

                for i, (cx, cy) in enumerate(sh_clipped):
                    self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill="#ef4444", outline="#22c55e", width=2)
                    self.canvas.create_text(cx + 8, cy + 8, text=f"C{i+1}", fill="#22c55e", font=("Consolas", 9, "bold"))

        if method in ("Cohen-Sutherland", "Dual Comparison"):
            for p1, p2, res, c1, c2 in cs_edges:
                if res is not None:
                    cx1, cy1, cx2, cy2 = res
                    self.canvas.create_line(cx1, cy1, cx2, cy2, fill="#38bdf8", width=4)
                    self.canvas.create_oval(cx1 - 4, cy1 - 4, cx1 + 4, cy1 + 4, fill="#38bdf8")
                    self.canvas.create_oval(cx2 - 4, cy2 - 4, cx2 + 4, cy2 + 4, fill="#38bdf8")

    def launch_interactive_pygame(self):
        import subprocess
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_clipping.py")
        subprocess.Popen([sys.executable, script_path])


def main():
    root = tk.Tk()
    app = ClippingDialogApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
