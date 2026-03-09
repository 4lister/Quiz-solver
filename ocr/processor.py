from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
import pytesseract
from PIL import Image


@dataclass
class OcrConfig:
    language: str = "rus+eng"
    engine: str = "tesseract"  # or "easyocr"
    min_confidence: int = 60


def preprocess_image(pil_image: Image.Image) -> np.ndarray:
    """
    Apply grayscale, adaptive thresholding, noise removal, and scaling to ~300 DPI.
    Returns an OpenCV (numpy) image suitable for OCR.
    """
    # Convert PIL → OpenCV BGR
    img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize to improve OCR (approximate 300 DPI scaling)
    scale_factor = 2.0
    gray = cv2.resize(
        gray,
        None,
        fx=scale_factor,
        fy=scale_factor,
        interpolation=cv2.INTER_CUBIC,
    )

    # Adaptive threshold (Otsu)
    _, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Noise removal: median blur
    denoised = cv2.medianBlur(thresh, 3)

    # Deskew using image moments
    coords = np.column_stack(np.where(denoised > 0))
    if coords.size:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = denoised.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        denoised = cv2.warpAffine(
            denoised,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

    return denoised


def run_tesseract(
    image_cv: np.ndarray,
    config: OcrConfig,
) -> str:
    """
    Run Tesseract OCR and return raw text.
    """
    custom_config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(
        image_cv, lang=config.language, config=custom_config
    )
    return text


def ocr_image(
    pil_image: Image.Image,
    config: Optional[OcrConfig] = None,
) -> str:
    """
    High-level OCR entry point: preprocess + Tesseract (primary engine).
    EasyOCR fallback can be added later as needed.
    """
    if config is None:
        config = OcrConfig()

    processed = preprocess_image(pil_image)
    if config.engine == "tesseract":
        return run_tesseract(processed, config)

    # Placeholder for EasyOCR integration
    return run_tesseract(processed, config)


__all__ = ["OcrConfig", "preprocess_image", "ocr_image"]

