import argparse
import os
import time
import logging
from dotenv import load_dotenv

from MillerLieblingskind.main import process_pdf

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "hotfolder.log")),
        logging.StreamHandler(),
    ],
)


def monitor_folder(
    folder: str,
    slack_token: str | None,
    slack_channel: str | None,
    tts: bool,
    interval: int,
    keep: bool,
) -> None:
    os.makedirs(folder, exist_ok=True)
    logging.info("Scanning '%s' every %ds for PDF files...", folder, interval)
    while True:
        for name in os.listdir(folder):
            if not name.lower().endswith(".pdf"):
                continue
            path = os.path.join(folder, name)
            if not os.path.isfile(path):
                continue
            try:
                summary = process_pdf(path, slack_token, slack_channel, tts, keep)
                logging.info("Processed %s", summary["pdf"])
            except Exception as exc:
                logging.exception("Failed to process %s: %s", path, exc)
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor a hotfolder for new PDF files")
    parser.add_argument("folder", nargs="?", default="hotfolder", help="Folder to monitor")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--slack-token", dest="slack_token", help="Slack API token")
    parser.add_argument("--slack-channel", dest="slack_channel", help="Slack channel ID")
    parser.add_argument("--tts", action="store_true", help="Read tasks aloud")
    parser.add_argument(
        "--keep", action="store_true", help="Keep original PDFs for debugging"
    )
    args = parser.parse_args()

    load_dotenv()
    args.slack_token = args.slack_token or os.getenv("SLACK_TOKEN")
    args.slack_channel = args.slack_channel or os.getenv("SLACK_CHANNEL")

    monitor_folder(
        args.folder,
        args.slack_token,
        args.slack_channel,
        args.tts,
        args.interval,
        args.keep,
    )


if __name__ == "__main__":
    main()

