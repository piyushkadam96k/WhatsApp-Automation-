import json
import os

CONTACTS_FILE = os.path.join(os.path.dirname(__file__), 'contacts.json')

def load_contacts():
    if not os.path.exists(CONTACTS_FILE):
        return {}
    try:
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading contacts: {e}")
        return {}

def get_phone_by_name(name):
    """
    Returns the phone number for a given name if it exists in contacts.json.
    Case-insensitive lookup.
    """
    contacts = load_contacts()
    # Normalize name for lookup
    name_lower = name.lower().strip()
    
    for contact_name, phone in contacts.items():
        if contact_name.lower().strip() == name_lower:
            return phone
    return None
