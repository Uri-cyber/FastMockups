"""
FastMockups - Advanced Bulk Product Mockup Generator
Supports shadows, perspective transforms, auto-detection, and cloud integration
"""

__version__ = "2.0.0"
__author__ = "FastMockups Team"

from .core import MockupGenerator
from .effects import ShadowEffect, PerspectiveEffect
from .formats import ExportManager
from .auto_detect import TemplateDetector

__all__ = [
    "MockupGenerator",
    "ShadowEffect",
    "PerspectiveEffect",
    "ExportManager",
    "TemplateDetector",
]
