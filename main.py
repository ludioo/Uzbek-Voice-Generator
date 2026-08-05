import argparse
import asyncio
import logging
from pathlib import Path

from src.ui import run_cli


def main() -> None:
    parser = argparse.ArgumentParser(description="Uzbek Voice Generator")
    parser.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Path to UTF-8 CSV with columns text,gender,filename",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    exit_code = asyncio.run(run_cli(args.csv))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
