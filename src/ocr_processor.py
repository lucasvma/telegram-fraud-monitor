import pytesseract
from PIL import Image
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

MAX_IMAGE_SIZE = (4000, 4000)
ALLOWED_FORMATS = {'JPEG', 'PNG', 'GIF', 'BMP', 'TIFF'}

def validate_image(image_path: str) -> bool:
    try:
        path = Path(image_path)
        
        if not path.exists():
            logger.error(f"Image file not found: {image_path}")
            return False
            
        if path.stat().st_size > 10 * 1024 * 1024:
            logger.error(f"Image file too large: {path.stat().st_size} bytes")
            return False
            
        with Image.open(image_path) as img:
            if img.format not in ALLOWED_FORMATS:
                logger.error(f"Unsupported image format: {img.format}")
                return False
                
            if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                logger.error(f"Image too large: {img.size}")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Image validation error: {e}")
        return False

def extract_text_from_image(image_path: str) -> str:
    try:
        if not validate_image(image_path):
            return ""
            
        custom_config = r'--oem 3 --psm 6'
        
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                
            text = pytesseract.image_to_string(img, config=custom_config, lang='eng+por')
            
            if len(text) > 2000:
                text = text[:2000] + "... [OCR truncated]"
                
            logger.info(f"OCR processed successfully, extracted {len(text)} characters")
            return text.strip()
            
    except pytesseract.TesseractError as e:
        logger.error(f"Tesseract OCR error: {e}")
        return ""
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        return ""