# WhatsApp Automation 🚀💬

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ A lightweight toolkit to automate WhatsApp Web using Playwright — send text & voice messages, manage contacts, and run bulk sends.

**Author:** Amit Kadam
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️ Setup

1) Install dependencies

```bash
pip install -r requirements.txt
python -m playwright install
```

2) Run the script (first run opens the browser to scan the QR code)

```bash
python send_whatsapp.py --phone 15551234567 --message "Hello from automation"
```

⚡ Quick start
```bash
# Basic send (first run opens browser to scan QR code)
python send_whatsapp.py --phone 15551234567 --message "Hello from automation"

# Use saved profile to avoid QR scan each time
python send_whatsapp.py --phone 15551234567 --message "Hi" --profile-dir ./playwright_userdata/Default
```

🧰 Core scripts & useful functions
- 📤 `send_whatsapp.py` — Send a single or repeated text message via WhatsApp Web.
  - Key options: `--phone`, `--name`, `--message`, `--repeat`, `--delay`, `--profile-dir`.
  - Example: `python send_whatsapp.py --phone 15551234567 --message "Hello" --repeat 3 --delay 2`

- 🖥️ `send_whatsapp_desktop.py` — Desktop automation (native app/window) when Playwright isn't preferred.
  - Example: `python send_whatsapp_desktop.py --name "Alice" --message "Hello from desktop script"`

- 📦 `send_whatsapp_auto.py` — Bulk sends from CSV/JSON contact lists and scheduling helpers.
  - Example: `python send_whatsapp_auto.py --contacts contacts.csv --message "Monthly update" --dry-run`

- 📇 `contacts_manager.py` — Manage contacts in `contacts.csv` and `contacts.json`.
  - Helpers: `load_contacts(path)`, `find_contact_by_name(contacts, name)`, `save_contacts(path, contacts)`

- 🎙️ `voice_whatsapp.py` — Send voice messages (record or file).
  - Example: `python voice_whatsapp.py --phone 15551234567 --file hello.ogg`

- 🧾 `csv_to_json.py` — Convert a CSV file to JSON (array or object keyed by a column).
  - Example: `python csv_to_json.py --input contacts.csv --output contacts.json`
  - Key option: `--key` to use a column value as the object key (e.g. `--key name`).

- 🧩 `csv_extractor_gui.py` — Simple Tkinter GUI to pick columns from a CSV and export a smaller CSV.
  - Run the GUI: `python csv_extractor_gui.py` (open a CSV, select columns, export).
  - No external packages required (Tkinter included with standard Python on most platforms).

📂 Contacts file formats
- `contacts.csv` (CSV with header `name,phone`):

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

💡 Examples
- Send to a contact by name (chat lookup):
```bash
python send_whatsapp.py --name "Alice" --message "Hello Alice!" --profile-dir ./playwright_userdata/Default
```

- Bulk send from CSV (dry run shows messages without sending):
```bash
python send_whatsapp_auto.py --contacts contacts.csv --message "Hello everyone" --dry-run
```

🎨 Tips & decorations
- Use `--profile-dir` pointing to `playwright_userdata/Default` to persist login and skip repeated QR scans.
- Use `--delay` and `--repeat` responsibly to mimic human behaviour and reduce rate-limiting risk.
- Test with `--dry-run` and small `--repeat` values before bulk sending.

🛠️ Troubleshooting
- QR not showing / login issues: remove `playwright_userdata/Default` to force fresh login, or ensure Playwright browsers are installed.
- Playwright errors: run `python -m playwright install` and check your Python environment.

🤝 Contributing
- Improvements, bug fixes and new script examples are welcome. Open an issue or submit a PR.

📝 License
- Use responsibly. This repository is provided as-is.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ Happy automating! 🚀
