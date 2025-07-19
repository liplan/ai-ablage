import argparse
import json
import os
import logging
from datetime import datetime

from utils.ocr_engine import pdf_to_text
from utils.document_classifier import classify_document
from utils.task_extractor import extract_tasks
from dotenv import load_dotenv

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "miller.log")),
        logging.StreamHandler(),
    ],
)

try:
    from slack_sdk import WebClient
except ImportError:
    WebClient = None

try:
    from gtts import gTTS
    from playsound import playsound
except ImportError:
    gTTS = None
    playsound = None

def save_document(pdf_path: str, doc_type: str) -> str:
    """Save the PDF to a structured folder hierarchy based on document type."""
    date_str = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    base_name = os.path.basename(pdf_path)
    new_name = f"{doc_type}_{date_str}_{base_name}"
    target_dir = os.path.join("archive", doc_type)
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, new_name)
    os.rename(pdf_path, target_path)
    return target_path

def send_slack_message(token: str, channel: str, text: str):
    if WebClient is None:
        logging.warning("slack_sdk is not installed. Skipping Slack message.")
        return
    client = WebClient(token=token)
    client.chat_postMessage(channel=channel, text=text)
    logging.info("Sent Slack message to %s", channel)

def speak_text(text: str):
    if gTTS is None or playsound is None:
        logging.warning("gTTS or playsound not installed. Skipping TTS playback.")
        return
    tts = gTTS(text=text, lang="de")
    filename = "speech.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)
    logging.info("Played TTS audio")


def process_pdf(
    pdf_path: str,
    slack_token: str | None = None,
    slack_channel: str | None = None,
    tts: bool = False,
) -> dict:
    """Process a single PDF document using the standard pipeline."""
    text = pdf_to_text(pdf_path)
    doc_type = classify_document(text)
    tasks = extract_tasks(text)

    archived_path = save_document(pdf_path, doc_type)

    tasks_json = json.dumps(tasks, indent=2, ensure_ascii=False)
    print(f"Dokumenttyp: {doc_type}")
    print(f"Gespeichert unter: {archived_path}")
    print("Gefundene Aufgaben:")
    print(tasks_json)

    if slack_token and slack_channel:
        message = f"Dokumenttyp: {doc_type}\nAufgaben: {tasks_json}"
        send_slack_message(slack_token, slack_channel, message)

    if tts:
        speak_text(tasks_json)

    summary = {
        "pdf": pdf_path,
        "archived": archived_path,
        "document_type": doc_type,
        "tasks": tasks,
    }
    logging.info("Processed %s as %s", pdf_path, archived_path)
    logging.info("Summary: %s", summary)
    with open(os.path.join(LOG_DIR, "summary.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(summary, ensure_ascii=False) + "\n")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Process a scanned PDF document.")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--slack-token", dest="slack_token", help="Slack API token")
    parser.add_argument("--slack-channel", dest="slack_channel", help="Slack channel ID")
    parser.add_argument("--tts", action="store_true", help="Read tasks aloud")
    args = parser.parse_args()

    load_dotenv()
    args.slack_token = args.slack_token or os.getenv("SLACK_TOKEN")
    args.slack_channel = args.slack_channel or os.getenv("SLACK_CHANNEL")

    summary = process_pdf(args.pdf, args.slack_token, args.slack_channel, args.tts)
    print("Zusammenfassung:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
