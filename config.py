"""
Configuration module for SilentSlides
Handles paths, settings, and Tesseract detection
"""

import os
import platform
from pathlib import Path

# Project directories
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "output"
THEMES_DIR = PROJECT_ROOT / "themes"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Create directories if they don't exist
OUTPUT_DIR.mkdir(exist_ok=True)
THEMES_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# Tesseract OCR configuration
def detect_tesseract_path():
    """Auto-detect Tesseract installation path"""
    system = platform.system()
    
    # Common installation paths
    common_paths = []
    
    if system == "Windows":
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME")),
        ]
    elif system == "Darwin":  # macOS
        common_paths = [
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract",
        ]
    else:  # Linux
        common_paths = [
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ]
    
    # Check if tesseract is in PATH
    import shutil
    tesseract_cmd = shutil.which("tesseract")
    if tesseract_cmd:
        return tesseract_cmd
    
    # Check common paths
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

TESSERACT_CMD = detect_tesseract_path()

# SentenceTransformers model
SENTENCE_TRANSFORMER_MODEL = "all-MiniLM-L6-v2"  # Lightweight, CPU-friendly

# OCR settings
OCR_LANGUAGE = "eng"  # Default language
OCR_CONFIG = "--oem 3 --psm 3"  # LSTM + Automatic page segmentation

# Clustering settings
MIN_CLUSTER_SIZE = 2
CLUSTERING_METHOD = "hdbscan"  # or "kmeans"
MAX_TOPICS = 10

# Slide generation settings
DEFAULT_THEME = "clean"
MAX_BULLETS_PER_SLIDE = 5
TITLE_SLIDE_ENABLED = True
SUMMARY_SLIDE_ENABLED = True

# Logging
LOG_LEVEL = "INFO"
