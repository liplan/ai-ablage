import argparse
import os
import time

from MillerLieblingskind.main import process_pdf


def monitor_folder(folder: str, slack_token: str | None, slack_channel: str | None, tts: bool, interval: int) -> None:
    os.makedirs(folder, exist_ok=True)
    print(f"Scanning '{folder}' every {interval}s for PDF files...")
    while True:
        for name in os.listdir(folder):
            if not name.lower().endswith(".pdf"):
                continue
            path = os.path.join(folder, name)
            if not os.path.isfile(path):
                continue
            try:
                process_pdf(path, slack_token, slack_channel, tts)
            except Exception as exc:
                print(f"Failed to process {path}: {exc}")
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor a hotfolder for new PDF files")
    parser.add_argument("folder", nargs="?", default="hotfolder", help="Folder to monitor")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--slack-token", dest="slack_token", help="Slack API token")
    parser.add_argument("--slack-channel", dest="slack_channel", help="Slack channel ID")
    parser.add_argument("--tts", action="store_true", help="Read tasks aloud")
    args = parser.parse_args()
    monitor_folder(args.folder, args.slack_token, args.slack_channel, args.tts, args.interval)


if __name__ == "__main__":
    main()

