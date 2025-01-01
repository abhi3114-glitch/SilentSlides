"""
OCR Engine for SilentSlides
Handles image preprocessing and text extraction using Tesseract
"""

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from typing import List, Dict, Tuple
import logging

from config import TESSERACT_CMD, OCR_LANGUAGE, OCR_CONFIG

# Configure Tesseract
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

logger = logging.getLogger(__name__)


class OCREngine:
    """OCR processing with image preprocessing"""
    
    def __init__(self, language: str = OCR_LANGUAGE):
        self.language = language
        self._check_tesseract()
    
    def _check_tesseract(self):
        """Verify Tesseract is installed"""
        try:
            pytesseract.get_tesseract_version()
            logger.info(f"Tesseract found: {TESSERACT_CMD}")
        except Exception as e:
            raise RuntimeError(
                "Tesseract not found. Please install Tesseract OCR:\n"
                "Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "Mac: brew install tesseract\n"
                "Linux: sudo apt-get install tesseract-ocr"
            ) from e
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Enhance image quality for better OCR accuracy
        - Convert to grayscale
        - Increase contrast
        - Reduce noise
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # Reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    
    def extract_text(self, image_path: str, preprocess: bool = True) -> Dict[str, any]:
        """
        Extract text from a single image
        
        Args:
            image_path: Path to image file
            preprocess: Whether to apply preprocessing
        
        Returns:
            Dict with 'text', 'confidence', 'details'
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Preprocess if enabled
            if preprocess:
                image = self.preprocess_image(image)
            
            # Extract text with details
            text = pytesseract.image_to_string(
                image, 
                lang=self.language,
                config=OCR_CONFIG
            )
            
            # Get confidence data
            data = pytesseract.image_to_data(
                image, 
                lang=self.language,
                config=OCR_CONFIG,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text.strip(),
                'confidence': round(avg_confidence, 2),
                'word_count': len(text.split()),
                'source': image_path
            }
            
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return {
                'text': '',
                'confidence': 0,
                'word_count': 0,
                'source': image_path,
                'error': str(e)
            }
    
    def batch_extract(self, image_paths: List[str], preprocess: bool = True) -> List[Dict]:
        """
        Extract text from multiple images
        
        Args:
            image_paths: List of image file paths
            preprocess: Whether to apply preprocessing
        
        Returns:
            List of extraction results
        """
        results = []
        for i, path in enumerate(image_paths):
            logger.info(f"Processing image {i+1}/{len(image_paths)}: {path}")
            result = self.extract_text(path, preprocess)
            results.append(result)
        
        return results
    
    def get_combined_text(self, results: List[Dict]) -> str:
        """Combine all extracted text into a single string"""
        return "\n\n".join([r['text'] for r in results if r['text']])


def check_tesseract_installation() -> Tuple[bool, str]:
    """
    Check if Tesseract is properly installed
    
    Returns:
        (is_installed, message)
    """
    if not TESSERACT_CMD:
        return False, (
            "Tesseract OCR not found. Please install:\n\n"
            "**Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki\n"
            "**Mac**: `brew install tesseract`\n"
            "**Linux**: `sudo apt-get install tesseract-ocr`"
        )
    
    try:
        version = pytesseract.get_tesseract_version()
        return True, f"Tesseract {version} found at: {TESSERACT_CMD}"
    except Exception as e:
        return False, f"Tesseract found but not working: {e}"
