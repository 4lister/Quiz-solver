from __future__ import annotations

import argparse
from pathlib import Path

from core.pipeline import (
    PipelineConfig,
    run_capture_ocr_once,
    run_full_pipeline_once,
)
from utils.logger import configure_logging, logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Real-Time Quiz Solver — M1 prototype (capture → OCR)."
    )
    parser.add_argument(
        "--monitor",
        type=int,
        default=1,
        help="Monitor index for capture (1 = primary).",
    )
    parser.add_argument(
        "--roi",
        type=int,
        nargs=4,
        metavar=("LEFT", "TOP", "WIDTH", "HEIGHT"),
        help="Optional ROI rectangle relative to selected monitor.",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Also отправить распознанный вопрос в Claude и показать ответ.",
    )
    parser.add_argument(
        "--provider",
        choices=["claude", "ollama"],
        default="claude",
        help="LLM провайдер: 'claude' (по умолчанию) или 'ollama' (локальная модель, без оплаты).",
    )
    return parser.parse_args()


def main() -> None:
    project_root = Path(__file__).resolve().parent
    configure_logging(project_root / "logs")

    args = parse_args()
    logger.info("Real-Time Quiz Solver (M1) starting")

    from capture.screen import CaptureConfig
    from ocr.processor import OcrConfig

    capture_cfg = CaptureConfig(
        monitor_index=args.monitor,
        roi=tuple(args.roi) if args.roi else None,
    )
    ocr_cfg = OcrConfig()

    pipeline_cfg = PipelineConfig(
        capture=capture_cfg,
        ocr=ocr_cfg,
        provider=args.provider,
        save_last_capture=True,
    )

    if args.llm:
        ocr_text, llm_answer = run_full_pipeline_once(
            pipeline_cfg,
            use_llm=True,
        )
    else:
        ocr_text = run_capture_ocr_once(pipeline_cfg)
        llm_answer = None

    print("\n===== OCR RESULT =====\n")
    print(ocr_text)
    print("======================\n")

    if llm_answer:
        print("===== CLAUDE ANSWER =====\n")
        print(llm_answer)
        print("=========================\n")


if __name__ == "__main__":
    main()

