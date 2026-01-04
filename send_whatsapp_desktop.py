#!/usr/bin/env python3
"""
Automate WhatsApp Desktop to send a message to a contact name using UI automation.
This script uses `pywinauto` to focus the WhatsApp window, open the search/new-chat box (Ctrl+K),
select the contact, and send the message.

Note: This is somewhat fragile and depends on WhatsApp Desktop keyboard shortcuts (Ctrl+K).
If Desktop automation fails, the script falls back to the web automation `send_whatsapp.py`.
"""
import argparse
import time
import sys
import os
import subprocess

try:
    from pywinauto import Desktop, Application
    from pywinauto.keyboard import send_keys
    import pyperclip
except Exception:
    print('pywinauto or pyperclip not installed; please run: pip install pywinauto pyperclip')
    # If pyperclip falls back, we might error out, so best to ensure it's there
    pass

# ... (omitted unaltered parts if any) ... but for now I will replace the imports and the function

def find_or_start_whatsapp():
    # Helper to find window
    def get_window():
        try:
            # Search for any window with 'WhatsApp' in the exact title or close match
            windows = Desktop(backend="uia").windows(title="WhatsApp", visible_only=False)
            if not windows:
                 # fallback to regex
                 windows = Desktop(backend="uia").windows(title_re=".*WhatsApp.*", visible_only=False)
            
            for w in windows:
                if w.is_visible():
                    return w
            if windows:
                return windows[0]
        except Exception:
            pass
        return None

    # 1. Try to find existing window
    win = get_window()
    if win:
        return win

    # 2. If not found, launch it
    print("WhatsApp not found. Launching via whatsapp://...")
    try:
        os.startfile('whatsapp://')
        # Wait for it to appear
        for _ in range(15): # wait up to 15 seconds
            time.sleep(1.0)
            win = get_window()
            if win:
                # Give it a moment to fully render
                time.sleep(2.0)
                return win
    except Exception as e:
        print(f"Failed to launch WhatsApp: {e}")
    
    return None


def send_message_desktop(name, message, repeat=1, delay=1.0):
    win = find_or_start_whatsapp()
    if not win:
        print('Could not find or start WhatsApp Desktop.')
        return False

    # Focus window (type_keys will also ensure focus)
    try:
        if win.is_minimized():
            win.restore()
        win.set_focus()
        time.sleep(0.5) # ensure focus settles
    except Exception:
        pass

    print('WhatsApp window found. Starting chat...')

    # Open New Chat (Ctrl+N), type name, select
    try:
        # Ctrl+N -> Reduced pause
        win.type_keys('^n', pause=1.0)
        
        # Type name -> Faster pause
        win.type_keys(name, with_spaces=True, pause=1.0)
        
        # Press Enter to select the contact -> Reduced wait for chat load
        # We assume 2.5s is enough for most modern PCs/connections. 
        # If it fails, we might need a retry, but speed is priority now.
        win.type_keys('{ENTER}', pause=2.0) 
        time.sleep(1.0) # wait for chat load
        
    except Exception as e:
        print('Failed to navigate/select contact:', e)
        return False

    print('Contact selected. Sending message...')

    # Type message and send
    try:
        # Check if message already typed (focus might be lost)
        # We just type blindly now
        
        for i in range(repeat):
             # Type message safely (no clipboard interference preferred)
             win.type_keys(message, with_spaces=True, pause=0.01) # fast typing
             
             win.type_keys('{ENTER}', pause=delay)
             
        return True
    except Exception as e:
        print('Failed to send message:', e)
        return False


def fallback_to_web(args):
    script = os.path.join(os.path.dirname(__file__), 'send_whatsapp.py')
    if not os.path.isfile(script):
        print('Web automation not available:', script)
        return 2
    cmd = [sys.executable, script]
    if args.name:
        cmd += ['--name', args.name]
    if args.phone:
        cmd += ['--phone', args.phone]
    cmd += ['--message', args.message]
    if args.repeat:
        cmd += ['--repeat', str(args.repeat)]
    if args.delay:
        cmd += ['--delay', str(args.delay)]
    if args.profile_dir:
        cmd += ['--profile-dir', args.profile_dir]
    return subprocess.run(cmd).returncode


def send_message_via_url_mode(repeat=1, delay=1.0):
    """
    Used when the chat is already opened via whatsapp:// scheme.
    Just waits for window and presses Enter.
    """
    win = find_or_start_whatsapp()
    if not win:
        print('Could not find WhatsApp window after URL launch.')
        return False

    try:
        if win.is_minimized():
            win.restore()
        win.set_focus()
        time.sleep(1.0) # wait for focus
    except Exception:
        pass

    print('WhatsApp window active. Waiting for chat to load/draft...')
    # Increased wait time to ensure the text is fully inserted by WhatsApp
    time.sleep(5.0) 

    # Method: VBScript fallback (Most robust for Windows UI automation)
    # If pywinauto fails to "convince" the app that Enter was pressed, wscript usually works.
    print("Attempting Send (Method: VBScript SendKeys)...")
    try:
        vbs_script = os.path.join(os.path.dirname(__file__), 'send_enter.vbs')
        with open(vbs_script, 'w') as f:
            f.write('Set WshShell = WScript.CreateObject("WScript.Shell")\n')
            f.write('WScript.Sleep 500\n') # wait a bit
            f.write('WshShell.SendKeys "{ENTER}"\n')
        
        # Run the VBS
        subprocess.run(['cscript', '//Nologo', vbs_script], check=False)
        
        # clean up
        try:
            os.remove(vbs_script)
        except:
            pass
            
        return True
    except Exception as e:
        print('Failed to send message via VBScript:', e)
        # Fallback to pywinauto just in case
        try:
             from pywinauto.keyboard import send_keys
             send_keys('{ENTER}')
        except:
             pass
        return True


def main():
    parser = argparse.ArgumentParser(description='Send WhatsApp Desktop message by contact name.')
    parser.add_argument('--phone', help='Phone number in international format (optional)')
    parser.add_argument('--name', help='Contact name as shown in WhatsApp')
    parser.add_argument('--message', required=True, help='Message text')
    parser.add_argument('--repeat', type=int, default=1)
    parser.add_argument('--delay', type=float, default=1.0)
    parser.add_argument('--profile_dir', default='./playwright_userdata')
    args = parser.parse_args()

    if not args.name and not args.phone:
        print('Provide --name (preferred) or --phone')
        return 1

    # prefer name (desktop flow supports name)
    ok = send_message_desktop(args.name or args.phone, args.message, args.repeat, args.delay)
    if not ok:
        print('Desktop automation failed, falling back to web.')
        return fallback_to_web(args)
    print('Message sent via WhatsApp Desktop.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
