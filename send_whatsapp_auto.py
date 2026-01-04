#!/usr/bin/env python3
"""
Wrapper: if WhatsApp Desktop installed, try to open desktop app via URL scheme; otherwise use web automation.
"""
import argparse
import os
import subprocess
import sys
from urllib.parse import quote


def open_desktop_whatsapp(phone, message):
    # Attempt to open via whatsapp:// URL scheme (may open Desktop app if registered)
    if not phone:
        print('Desktop automation with name is not supported; fallback to web.')
        return False
    url = f'whatsapp://send?phone={phone}&text={quote(message)}'
    try:
        os.startfile(url)
        return True
    except Exception as e:
        print('Could not open whatsapp:// URL scheme:', e)
        return False


def run_web_script(args):
    script = os.path.join(os.path.dirname(__file__), 'send_whatsapp.py')
    if not os.path.isfile(script):
        print('Web automation script not found:', script)
        return 2
    cmd = [sys.executable, script]
    if args.phone:
        cmd += ['--phone', args.phone]
    if args.name:
        cmd += ['--name', args.name]
    cmd += ['--message', args.message]
    if args.repeat and args.repeat != 1:
        cmd += ['--repeat', str(args.repeat)]
    if args.delay and args.delay != 1.0:
        cmd += ['--delay', str(args.delay)]
    if args.profile_dir:
        cmd += ['--profile-dir', args.profile_dir]
    if getattr(args, 'browser_lnk', None):
        cmd += ['--browser-lnk', args.browser_lnk]
    if getattr(args, 'dry_run', None):
        cmd += ['--dry-run']
    proc = subprocess.run(cmd)
    return proc.returncode


def main():
    parser = argparse.ArgumentParser(description='Auto-choose Desktop or Web WhatsApp automation.')
    parser.add_argument('--phone', help='Phone number in international format, e.g. 15551234567')
    parser.add_argument('--name', help='Contact name as it appears in WhatsApp')
    parser.add_argument('--message', required=False, help='Message text to send (if omitted, you will be prompted)')
    parser.add_argument('--repeat', type=int, default=1, help='How many times to send the message')
    parser.add_argument('--delay', type=float, default=1.0, help='Seconds between repeated messages')
    parser.add_argument('--profile-dir', dest='profile_dir', default='./playwright_userdata', help='Profile dir (web)')
    parser.add_argument('--browser-lnk', dest='browser_lnk', help='Path to a .lnk shortcut pointing to the browser to use (optional)')
    parser.add_argument('--dry-run', dest='dry_run', action='store_true', help='Open chat and fill message but do not send')
    args = parser.parse_args()

    # Prompt for contact if missing
    if not args.name and not args.phone:
        try:
            contact = input('Enter contact name or phone (digits for phone): ').strip()
        except Exception:
            print('No contact provided; aborting.')
            return 1
        if not contact:
            print('Empty contact; aborting.')
            return 1
        digits = ''.join(ch for ch in contact if ch.isdigit())
        if digits and len(digits) >= 6:
            args.phone = digits
        else:
            args.name = contact

    # Prompt for message if missing
    if not args.message:
        try:
            args.message = input('Enter message to send: ').strip()
        except Exception:
            print('No message provided; aborting.')
            return 1
        if not args.message:
            print('Empty message; aborting.')
            return 1

    # Try to use Desktop automation first
    use_desktop = True
    try:
        from send_whatsapp_desktop import send_message_desktop, send_message_via_url_mode
    except ImportError:
        print('Could not import send_whatsapp_desktop; falling back to web.')
        use_desktop = False
    
    # Try smart lookup
    try:
        import contacts_manager
        smart_phone = contacts_manager.get_phone_by_name(args.name) if args.name else None
    except Exception as e:
        print('Error in smart lookup:', e)
        smart_phone = None

    if use_desktop:
        # 1. Smart Send Mode (if contact found in json)
        if smart_phone:
            print(f'Smart Lookup: Found "{args.name}" -> {smart_phone}')
            print('Opening direct chat via URL...')
            # This opens the app and sets up the message
            if open_desktop_whatsapp(smart_phone, args.message):
                # Just need to press Enter now
                if send_message_via_url_mode(args.repeat, args.delay):
                    print('Message sent via Smart Send.')
                    return 0
                else:
                     print('Smart Send (Enter) failed; attempting manual search...')
            else:
                print('Smart Send (URL) open failed; attempting manual search...')
        
        # 2. Search Mode (Fallback or default if name not in json)
        print('Attempting to send via WhatsApp Desktop (Search Mode)...')
        ok = send_message_desktop(args.name or args.phone, args.message, args.repeat, args.delay)
        if ok:
             print('Message sent via WhatsApp Desktop.')
             return 0
        print('Desktop automation failed — falling back to web automation.')
        
    return run_web_script(args)


if __name__ == '__main__':
    sys.exit(main())
