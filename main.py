"""
main.py

Entry point for Auto File Organizer:
- Parses CLI args
- Either schedules polling or starts real-time watch
- Generates LLM-based suggestions
- Applies file operations (rename/move/delete)
"""
import argparse
import time
import schedule
import logging

from file_scanner import load_config, scan_directories
from organizer import suggest_actions
from utils import apply_suggestion
from file_watcher import start_watcher


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Auto File Organizer Agent")
    parser.add_argument(
        "-c", "--config", default="config.yaml",
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run a single scan and exit"
    )
    parser.add_argument(
        "--watch", action="store_true",
        help="Use real-time monitoring via watchdog"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Log suggestions without applying file operations"
    )
    parser.add_argument(
        "--auto-confirm", action="store_true",
        help="Skip user confirmation prompts"
    )
    return parser.parse_args()


def job(config: dict, dry_run: bool = False) -> None:
    """
    Scan directories, generate suggestions, and apply or log actions.

    :param config: Configuration dict from config.yaml
    :param dry_run: If True, do not apply file operations.
    """
    files = scan_directories(config)
    logging.info(f"Scanned {len(files)} files.")

    auto_confirm = config.get('auto_confirm', False)
    root_folder = config.get('root_folder')

    for file_meta in files:
        suggestion = suggest_actions(file_meta)
        logging.info(
            f"File: {file_meta['name']} | "
            f"Rename → {suggestion.get('suggested_name')} | "
            f"Move → {suggestion.get('suggested_folder')} | "
            f"Delete? {suggestion.get('delete')}"
        )
        if not dry_run:
            apply_suggestion(
                file_meta,
                suggestion,
                root_folder=root_folder,
                auto_confirm=auto_confirm
            )


def main() -> None:
    """
    Main entry: parse args, configure logging, and dispatch mode.
    """
    args = parse_args()
    config = load_config(args.config)

    # Override auto_confirm from CLI
    if args.auto_confirm:
        config['auto_confirm'] = True

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('logs/actions.log'),
            logging.StreamHandler()
        ]
    )
    logging.info("Starting Auto File Organizer Agent")

    # Real-time watch mode
    if args.watch:
        logging.info("Entering watch mode (real-time monitoring)")
        start_watcher(config, dry_run=args.dry_run)
        return

    # One-off execution
    if args.once:
        logging.info("Running single scan (once)")
        job(config, dry_run=args.dry_run)
        return

    # Scheduled polling mode
    interval = config.get('check_interval_minutes', 10)
    logging.info(f"Scheduling scans every {interval} minutes")
    job(config, dry_run=args.dry_run)  # initial run
    schedule.every(interval).minutes.do(job, config, args.dry_run)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Auto File Organizer stopped by user.")


if __name__ == '__main__':
    main()
