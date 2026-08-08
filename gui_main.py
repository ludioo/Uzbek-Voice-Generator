import logging

from src.ui.gui import run_gui


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    run_gui()


if __name__ == "__main__":
    main()
