"""CLI entrypoint for the weekly briefing pipeline."""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from src.codex_assisted import build_from_manifest
from src.config import API_AUTO_MODE, CODEX_ASSISTED_MODE, load_settings
from src.orchestrator import WeeklyBriefingOrchestrator, make_run_id, next_output_path


def main() -> int:
    """Run the CLI."""
    load_dotenv()
    args = parse_args()
    settings = load_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    orchestrator = WeeklyBriefingOrchestrator(settings)
    if args.mode == CODEX_ASSISTED_MODE:
        if args.manifest is None:
            raise SystemExit("--manifest is required in codex_assisted mode")
        output_path = args.output or next_output_path(settings.output_dir)
        result = build_from_manifest(
            args.manifest,
            output_path,
            run_id=make_run_id(),
        )
    else:
        result = asyncio.run(
            orchestrator.run(
                upload_dir=args.upload_dir,
                output_path=args.output,
            )
        )
    logging.info(
        "briefing generated: output=%s xlsx=%s run_id=%s slides=%d",
        result.output_path,
        result.xlsx_path,
        result.run_id,
        result.slide_count,
    )
    return 0


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a construction weekly briefing PPTX.",
    )
    parser.add_argument(
        "--mode",
        choices=(CODEX_ASSISTED_MODE, API_AUTO_MODE),
        default=None,
        help="Run mode. Defaults to BRIEFING_RUN_MODE or codex_assisted.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Codex-assisted briefing manifest JSON.",
    )
    parser.add_argument(
        "--upload-dir",
        type=Path,
        default=Path("uploads"),
        help="Directory containing uploaded PDF files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output PPTX path under data/output. Defaults to next briefing filename.",
    )
    args = parser.parse_args()
    settings = load_settings()
    if args.mode is None:
        args.mode = settings.run_mode
    return args


if __name__ == "__main__":
    raise SystemExit(main())
