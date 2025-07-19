import argparse
import json
import os
from datetime import datetime

from utils.ocr_engine import pdf_to_text
from utils.document_classifier import classify_document
from utils.task_extractor import extract_tasks

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
        print("slack_sdk is not installed. Skipping Slack message.")
        return
    client = WebClient(token=token)
    client.chat_postMessage(channel=channel, text=text)

def speak_text(text: str):
    if gTTS is None or playsound is None:
        print("gTTS or playsound not installed. Skipping TTS playback.")
        return
    tts = gTTS(text=text, lang="de")
    filename = "speech.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

def main():
    parser = argparse.ArgumentParser(description="Process a scanned PDF document.")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--slack-token", help="Slack API token", dest="slack_token")
    parser.add_argument("--slack-channel", help="Slack channel ID", dest="slack_channel")
    parser.add_argument("--tts", action="store_true", help="Read tasks aloud")
    args = parser.parse_args()

    text = pdf_to_text(args.pdf)
    doc_type = classify_document(text)
    tasks = extract_tasks(text)

    archived_path = save_document(args.pdf, doc_type)

    tasks_json = json.dumps(tasks, indent=2, ensure_ascii=False)
    print(f"Dokumenttyp: {doc_type}")
    print(f"Gespeichert unter: {archived_path}")
    print("Gefundene Aufgaben:")
    print(tasks_json)

    if args.slack_token and args.slack_channel:
        message = f"Dokumenttyp: {doc_type}\nAufgaben: {tasks_json}"
        send_slack_message(args.slack_token, args.slack_channel, message)

    if args.tts:
        speak_text(tasks_json)

if __name__ == "__main__":
    main()
