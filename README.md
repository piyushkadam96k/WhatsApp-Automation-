# WhatsApp Automation 

Simple script to send WhatsApp messages automatically via WhatsApp Web using Playwright.

Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
python -m playwright install
```

2. Run the script (first run will open a browser to scan the QR code):

```bash
python send_whatsapp.py --phone 15551234567 --message "Hello from automation"
```

🎯 **WhatsApp Automation (Playwright)**

**Author:** Amit Kadam

══════════════════════════════════════════════════════
✨ A small toolkit to send WhatsApp messages via WhatsApp Web using Playwright. Useful scripts and functions included to manage contacts and send messages (text or voice).
══════════════════════════════════════════════════════

Prerequisites
- Python 3.8+
- `pip` and Playwright browser binaries

Installation
```bash
pip install -r requirements.txt
python -m playwright install
```

Quick start
```bash
# Basic send (first run opens browser to scan QR code)
python send_whatsapp.py --phone 15551234567 --message "Hello from automation"

# Use saved profile to avoid QR scan each time
python send_whatsapp.py --phone 15551234567 --message "Hi" --profile-dir ./playwright_userdata/Default
```

Core scripts & useful functions
- `send_whatsapp.py`: Send a single or repeated text message via WhatsApp Web.
	- Key options: `--phone`, `--name`, `--message`, `--repeat`, `--delay`, `--profile-dir`.
	- Example: `python send_whatsapp.py --phone 15551234567 --message "Hello" --repeat 3 --delay 2`

- `send_whatsapp_desktop.py`: Uses desktop automation (e.g., native app/window) — useful when Playwright is not preferred.
	- Example usage: `python send_whatsapp_desktop.py --name "Alice" --message "Hello from desktop script"`

- `send_whatsapp_auto.py`: Higher-level automation for bulk sends with CSV/JSON contact lists and scheduling helpers.
	- Example: `python send_whatsapp_auto.py --contacts contacts.csv --message "Monthly update" --dry-run`

- `contacts_manager.py`: Manage contacts stored in `contacts.csv` and `contacts.json` (import/export, add, remove, lookup).
	- Useful functions:
		- `load_contacts(path)` — returns a list of contact dicts.
		- `find_contact_by_name(contacts, name)` — returns a contact or `None`.
		- `save_contacts(path, contacts)` — updates disk copy.

- `voice_whatsapp.py`: Send voice messages (records audio or uses a file) via WhatsApp Web flow.
	- Example: `python voice_whatsapp.py --phone 15551234567 --file hello.ogg`

Contacts file formats
- `contacts.csv` (simple CSV): header `name,phone` and rows like:

```csv
name,phone
Alice,15550001111
Bob,15550002222
```

- `contacts.json` (array of objects):

```json
[
	{"name": "Alice", "phone": "15550001111"},
	{"name": "Bob", "phone": "15550002222"}
]
```

Examples
- Send to a contact by name (uses chat lookup):
```bash
python send_whatsapp.py --name "Alice" --message "Hello Alice!" --profile-dir ./playwright_userdata/Default
```

- Bulk send from CSV (dry run shows messages without sending):
```bash
python send_whatsapp_auto.py --contacts contacts.csv --message "Hello everyone" --dry-run
```

Tips & Decorations
- Add `--profile-dir` pointing to `playwright_userdata/Default` to persist login and skip repeated QR scans.
- Use `--delay` and `--repeat` responsibly to mimic human behavior and reduce the chance of rate-limiting.
- When testing, use small `--repeat` values and `--dry-run` where available.

Troubleshooting
- QR not showing / login issues: delete `playwright_userdata/Default` and re-run to force fresh login, or ensure Playwright browsers installed.
- Playwright errors: run `python -m playwright install` and verify your Python environment.

Contributing
- Improvements, bug fixes and new script examples are welcome. Open an issue or submit a PR in your repo.

License
- Use responsibly. This repository is provided as-is.

══════════════════════════════════════════════════════
Happy automating! 🚀
