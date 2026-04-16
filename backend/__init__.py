"""
Lako Backend Package
A proximity-based vendor discovery platform with OSM maps, heatmaps, and real-time chat.
"""

__version__ = "1.0.0"
__author__ = "Lako Team"

from .config import config
from .database import db
from .auth import Auth