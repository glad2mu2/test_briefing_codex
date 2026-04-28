"""CLI entrypoint for the weekly briefing pipeline."""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from src.config import load_settings
from src.orchestrator import WeeklyBriefingOrchestrator


def main() -> int:
    """Run the CLI."""
    load_dotenv()
    args = parse_args()
    settings = load_settings()
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    orchestrator = WeeklyBriefingOrchestrator(settings)
    result = asyncio.run(
        orchestrator.run(
            upload_dir=args.upload_dir,
            output_path=args.output,
        )
    )
    logging.info(
        "briefing generated: output=%s run_id=%s slides=%d",
        result.output_path,
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
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
