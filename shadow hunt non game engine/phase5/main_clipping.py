"""
Phase 5 — Main Polygon & Line Clipping Runner
==============================================
Runs the interactive Polygon & Line Clipping suite where you can:
- Select polygon types: Triangle, Rectangle, Convex Pentagon, Concave Star,
  Vision Cone, Arrow, or enter Custom Vertices
- Choose clipping methods:
    1. Sutherland-Hodgman Polygon Clipping (Closed Polygon)
    2. Cohen-Sutherland Line Clipping (Edge-by-Edge with 4-bit Outcodes)
    3. Dual Comparison (Simultaneous overlay)
- Customize or drag Viewport window boundaries [xmin, ymin, xmax, ymax]
- Step through the Sutherland-Hodgman 4-stage pipeline (Left, Right, Top, Bottom)
- Inspect 4-bit Outcodes for all 9 spatial regions in real-time
All implemented using Phase 5 core algorithms from cg_math.py!
"""

import sys
import os

# Ensure the phase5 directory is in the import path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from clipping_visualizer import run_interactive_clipping_demo

if __name__ == "__main__":
    run_interactive_clipping_demo()
