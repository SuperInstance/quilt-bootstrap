"""quilt-bootstrap — bring up the Quilt fleet in a fresh sandbox.

A single command clones, installs, and links every walker in the fleet.
Designed for use in fresh sandboxes (post-wipe restoration) or new
developer onboarding.

Three modes:
  - minimal: just the 7 core repos (no GPU/visual stack)
  - full: all 9 repos including brews + perception
  - demo: just enough to run the organism landing page

Usage:
    python3 -m quilt_bootstrap [--mode {minimal,full,demo}] [--prefix /workspace]
"""
from .bootstrap import bootstrap, check_status, MODES, FLEET, LINKED_WALKERS

__version__ = "0.1.0"
__all__ = ["bootstrap", "check_status", "MODES", "FLEET", "LINKED_WALKERS"]
