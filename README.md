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

### Zusätzliche Abhängigkeiten

Für die OCR muss das Tesseract-Binary installiert sein. Unter Debian/Ubuntu
lässt es sich mit

```bash
sudo apt-get install tesseract-ocr
```

installieren. Auf macOS kann stattdessen `brew install tesseract` verwendet
werden. Achte darauf, dass das `tesseract`-Kommando im `PATH` liegt, damit
`pytesseract` es finden kann. Zusätzlich wird das Sprachpaket `deu` benötigt.
Unter Debian/Ubuntu lässt es sich beispielsweise mit

```bash
sudo apt-get install tesseract-ocr-deu
```

installieren. Bei Homebrew befindet es sich bereits in `$(brew --prefix)/share/tessdata`.
Falls Tesseract das Datenverzeichnis nicht selbst findet, setze die Umgebungs-
variable `TESSDATA_PREFIX` auf den Pfad zu diesem Ordner. Das Skript versucht
die Variable beim Start nun automatisch auf einen Ordner zu setzen, in dem sich
die Datei `deu.traineddata` befindet. Ist sie nirgends auffindbar, wird eine
aussagekräftige Fehlermeldung ausgegeben.

### Hotfolder verwenden

Mit `hotfolder.py` lässt sich ein Ordner überwachen, in den neue PDF-Dateien gelegt werden. Jede gefundene Datei wird einmalig verarbeitet und anschließend archiviert. Beispiel:

```bash
python hotfolder.py /pfad/zum/hotfolder --interval 10
```

### Konfiguration

Leg eine Datei `.env` im Projektverzeichnis an und fülle sie nach dem Vorbild von `.env.example` aus. Dort werden Slack-Zugangsdaten hinterlegt, die von den Skripten automatisch geladen werden.

### Logging

Während der Verarbeitung werden Protokolle und Zusammenfassungen unter `logs/` abgelegt.
