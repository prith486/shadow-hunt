import sys
import os
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)
from clipping_visualizer import run_interactive_clipping_demo
if __name__ == '__main__':
    run_interactive_clipping_demo()
