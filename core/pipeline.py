from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image

from capture.screen import CaptureConfig, capture_screen
from ocr.processor import OcrConfig, ocr_image
from utils.logger import logger
from llm.client import (
    ClaudeConfig,
    OllamaConfig,
    ask_claude_for_quiz,
    ask_ollama_for_quiz,
)


@dataclass
class PipelineConfig:
    capture: CaptureConfig = field(default_factory=CaptureConfig)
    ocr: OcrConfig = field(default_factory=OcrConfig)
    claude: ClaudeConfig = field(default_factory=ClaudeConfig)
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    provider: str = "claude"  # "claude" or "ollama"
    save_last_capture: bool = False
    save_dir: Optional[Path] = None


def run_capture_ocr_once(
    pipeline_config: Optional[PipelineConfig] = None,
) -> str:
    """
    Simple synchronous pipeline for M1:
    capture → preprocess + OCR → text.
    """
    if pipeline_config is None:
        pipeline_config = PipelineConfig()

    logger.info("Starting capture → OCR pipeline (single-shot)")

    pil_img: Image.Image = capture_screen(pipeline_config.capture)
    logger.info("Screen captured; starting OCR")

    if pipeline_config.save_last_capture:
        save_dir = pipeline_config.save_dir or (Path.cwd() / "captures")
        save_dir.mkdir(parents=True, exist_ok=True)
        from datetime import datetime  # local import to avoid global dependency

        filename = datetime.now().strftime("capture_%Y%m%d_%H%M%S.png")
        save_path = save_dir / filename
        pil_img.save(save_path)
        logger.info("Saved screenshot to {}", save_path)

    text = ocr_image(pil_img, pipeline_config.ocr)
    logger.info("OCR finished; text length={}", len(text))

    return text


def run_full_pipeline_once(
    pipeline_config: Optional[PipelineConfig] = None,
    use_llm: bool = False,
) -> Tuple[str, Optional[str]]:
    """
    Захват → OCR → (опционально) запрос к Claude.
    Возвращает пару (ocr_text, llm_answer_text | None).
    """
    if pipeline_config is None:
        pipeline_config = PipelineConfig()

    ocr_text = run_capture_ocr_once(pipeline_config)

    llm_answer: Optional[str] = None
    if use_llm:
        logger.info("Invoking Claude for answer")
        try:
            if pipeline_config.provider == "claude":
                llm_answer = ask_claude_for_quiz(
                    ocr_text,
                    pipeline_config.claude,
                )
            elif pipeline_config.provider == "ollama":
                llm_answer = ask_ollama_for_quiz(
                    ocr_text,
                    pipeline_config.ollama,
                )
            else:
                logger.warning(
                    "Unknown LLM provider '{}', skipping LLM step",
                    pipeline_config.provider,
                )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to get answer from Claude: {}", exc)
            # Graceful degradation: return only OCR text when LLM is unavailable
            return ocr_text, None

    return ocr_text, llm_answer


__all__ = ["PipelineConfig", "run_capture_ocr_once", "run_full_pipeline_once"]

