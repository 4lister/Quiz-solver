from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional

import mss
from PIL import Image


@dataclass
class CaptureConfig:
    monitor_index: int = 1  # 1 = primary in mss
    # ROI as (left, top, width, height); if None, capture full monitor
    roi: Optional[Tuple[int, int, int, int]] = None


def capture_screen(config: CaptureConfig) -> Image.Image:
    """
    Capture a screenshot using mss.
    If roi is None, captures the full selected monitor.
    Returns a PIL Image.
    """
    with mss.mss() as sct:
        monitors = sct.monitors
        if config.monitor_index < 1 or config.monitor_index >= len(monitors):
            raise ValueError(f"Invalid monitor index {config.monitor_index}")

        mon = monitors[config.monitor_index]

        if config.roi is None:
            bbox = {
                "left": mon["left"],
                "top": mon["top"],
                "width": mon["width"],
                "height": mon["height"],
            }
        else:
            left, top, width, height = config.roi
            bbox = {
                "left": mon["left"] + left,
                "top": mon["top"] + top,
                "width": width,
                "height": height,
            }

        screenshot = sct.grab(bbox)
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        return img


__all__ = ["CaptureConfig", "capture_screen"]

