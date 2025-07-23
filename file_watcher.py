import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from file_scanner import load_config, scan_directories
from organizer import suggest_actions
from utils import apply_suggestion

class ChangeHandler(FileSystemEventHandler):
    """
    Handler for filesystem events that triggers the organizing job.
    """
    def __init__(self, config, dry_run=False, custom_prompt=None):
        super().__init__()
        self.config = config
        self.dry_run = dry_run
        self.custom_prompt = custom_prompt
        self.auto_confirm = config.get('auto_confirm', False)
        self.root_folder = config.get('root_folder')

    def on_any_event(self, event):  # covers create, modify, move, delete
        logging.info(f"Detected filesystem event: {event.event_type} - {event.src_path}")
        self.run_job()

    def run_job(self):
        files = scan_directories(self.config)
        logging.info(f"[Watcher] Scanned {len(files)} files.")
        for file_meta in files:
            suggestion = suggest_actions(file_meta, custom_prompt=self.custom_prompt)
            logging.info(
                f"[Watcher] File: {file_meta['name']} | "
                f"Rename → {suggestion.get('suggested_name')} | "
                f"Move → {suggestion.get('suggested_folder')} | "
                f"Delete? {suggestion.get('delete')}"
            )
            if not self.dry_run:
                apply_suggestion(
                    file_meta,
                    suggestion,
                    root_folder=self.root_folder,
                    auto_confirm=self.auto_confirm
                )


def start_watcher(config, dry_run=False, custom_prompt=None):
    """
    Start the watchdog observer for real-time monitoring.

    :param config: Configuration dict from config.yaml
    :param dry_run: If True, suggestions are logged but not applied.
    :param custom_prompt: Optional custom prompt text for file organization
    """
    paths = config.get('monitor_folders', [])
    event_handler = ChangeHandler(config, dry_run=dry_run, custom_prompt=custom_prompt)
    observer = Observer()

    for path in paths:
        observer.schedule(event_handler, path, recursive=False)
        logging.info(f"Watching directory: {path}")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("File watcher stopped by user.")
    observer.join()
