import argparse
import json
import os
import logging
from datetime import datetime
import shutil
import re

try:
    from PyPDF2 import PdfReader
except ImportError:  # pragma: no cover - optional dependency
    PdfReader = None

# Support execution both as a script and as a module
if __package__:
    # Imported via "MillerLieblingskind.main" - use relative imports
    from .utils.ocr_engine import pdf_to_text
    from .utils.document_classifier import classify_document
    from .utils.task_extractor import extract_tasks
else:
    # Executed directly - fall back to absolute imports
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


def get_pdf_author(pdf_path: str) -> str:
    """Return the author of ``pdf_path`` if available."""
    if PdfReader is None:
        return "Unknown"
    try:
        reader = PdfReader(pdf_path)
        info = reader.metadata
        author = getattr(info, "author", None)
    except Exception:  # pragma: no cover - best effort
        author = None
    if not author:
        return "Unknown"
    return str(author)


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Return a naive summary consisting of the first ``max_sentences``."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:max_sentences]).strip()

def _sanitize_filename(name: str) -> str:
    """Return a filesystem friendly version of ``name``."""
    name = re.sub(r"[^a-zA-Z0-9_.-]", "_", name)
    return name


def save_document(pdf_path: str, doc_type: str, author: str, keep: bool) -> str:
    """Save ``pdf_path`` to ``archive/author`` with a unique short filename."""
    date_str = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    base_name = os.path.basename(pdf_path)
    base_name = _sanitize_filename(base_name)
    new_name = f"{doc_type}_{date_str}_{base_name}"
    if len(new_name) > 32:
        new_name = new_name[:32]
    target_dir = os.path.join("archive", _sanitize_filename(author))
    os.makedirs(target_dir, exist_ok=True)
    target_path = os.path.join(target_dir, new_name)
    if keep:
        shutil.copy2(pdf_path, target_path)
    else:
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
    keep: bool = False,
) -> dict:
    """Process a single PDF document using the standard pipeline.

    When ``keep`` is ``True`` the source PDF is not removed so it can be
    processed multiple times for debugging or testing.
    """
    text = pdf_to_text(pdf_path)
    doc_type = classify_document(text)
    tasks = extract_tasks(text)
    author = get_pdf_author(pdf_path)

    archived_path = save_document(pdf_path, doc_type, author, keep)
    summary_text = summarize_text(text)

    tasks_json = json.dumps(tasks, indent=2, ensure_ascii=False)
    print(f"Dokumenttyp: {doc_type}")
    print(f"Gespeichert unter: {archived_path}")
    print("Gefundene Aufgaben:")
    print(tasks_json)
    print("Kurze Zusammenfassung:")
    print(summary_text)

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
        "author": author,
        "summary": summary_text,
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
    parser.add_argument(
        "--keep", action="store_true", help="Keep original PDF for debug/testing"
    )
    args = parser.parse_args()

    load_dotenv()
    args.slack_token = args.slack_token or os.getenv("SLACK_TOKEN")
    args.slack_channel = args.slack_channel or os.getenv("SLACK_CHANNEL")

    summary = process_pdf(
        args.pdf, args.slack_token, args.slack_channel, args.tts, args.keep
    )
    print("Zusammenfassung:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
