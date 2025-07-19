# ai-ablage
AI featured tool to organize the daily papershit

## MillerLieblingskind

Dieses Unterprojekt analysiert eingescannte PDF-Dokumente automatisch. Es demonstriert einen einfachen Ablauf von OCR bis zum Versand einer Slack-Nachricht.

### Struktur
- `main.py` – Einstiegspunkt
- `hotfolder.py` – Beobachtet einen Ordner und verarbeitet automatisch neue PDFs
- `utils/ocr_engine.py` – OCR von PDF-Dateien
- `utils/document_classifier.py` – Einfache Dokumentklassifizierung
- `utils/task_extractor.py` – Extraktion von Aufgaben und Fristen
- `requirements.txt` – Benötigte Python-Pakete

### Hotfolder verwenden

Mit `hotfolder.py` lässt sich ein Ordner überwachen, in den neue PDF-Dateien gelegt werden. Jede gefundene Datei wird einmalig verarbeitet und anschließend archiviert. Beispiel:

```bash
python hotfolder.py /pfad/zum/hotfolder --interval 10
```
