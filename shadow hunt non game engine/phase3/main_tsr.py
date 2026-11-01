"""
Phase 3 — Main 2D Transformation Runner (TSR & Composite)
=========================================================
Runs the interactive 2D transformation suite where you can:
- Enter original polygon vertices (e.g. triangle, rectangle)
- Choose Homogeneous Representation (Row Matrix vs Column Matrix)
- Apply Translation (T), Scaling (S), Rotation (R), or Composite (TSR)
- See computed 3x3 matrices & transformed coordinates in the console
- See real-time visual output with original (white) and transformed (cyan) shapes
  rendered using Bresenham's algorithms with vector displacement lines.
"""

import sys
import os

# Ensure the phase3 directory is in the import path
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from transforms import run_interactive_tsr_demo

if __name__ == "__main__":
    run_interactive_tsr_demo()
