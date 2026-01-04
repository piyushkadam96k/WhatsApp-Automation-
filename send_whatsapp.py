from playwright.sync_api import sync_playwright
from urllib.parse import quote
import argparse
import time
import os


def send_by_phone(page, phone, message, dry_run=False):
    url = f"https://web.whatsapp.com/send?phone={phone}&text={quote(message)}"
    page.goto(url)
    # give WhatsApp Web time to load the chat
    try:
        page.wait_for_selector('div[role="textbox"], div[contenteditable="true"]', timeout=15000)
    except Exception:
        # fallback short wait
        page.wait_for_timeout(3000)

    # Try to find the editable message box and send the message
    msg_selectors = [
        'div[contenteditable="true"][data-tab]',
        'div[contenteditable="true"]',
        'div[role="textbox"]'
    ]
    
    # helper to find any of the selectors
    msg_box = None
    for sel in msg_selectors:
        try:
            # reduced timeout for each check
            page.wait_for_selector(sel, state='visible', timeout=2000)
            msg_box = sel
            break
        except Exception:
            continue
            
    if msg_box:
        try:
            page.click(msg_box)
            try:
                page.focus(msg_box)
            except Exception:
                pass
            
            # Type message
            page.keyboard.type(message)
            
            if dry_run:
                return True
                
            # press Enter to send
            page.keyboard.press("Enter")
            # wait for send tick or just a small buffer
            page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"Error interacting with message box: {e}")
            pass

    # Try clicking the send button if available (fallback)
    try:
        btn = page.query_selector('button[aria-label="Send"], span[data-icon="send"]')
        if btn:
            btn.click()
            page.wait_for_timeout(1000)
            return True
    except Exception:
        pass

    print("Error: could not send message by phone; UI selectors not found.")
    return False


def send_by_name(page, name, message, dry_run=False):
    # open search, type name, press Enter
    search_selectors = [
        'div[contenteditable="true"][data-tab="3"]', # Search box often has data-tab 3
        'div[title="Search input textbox"]',
        'div[role="textbox"]'
    ]
    
    found_search = False
    for sel in search_selectors:
        try:
            page.wait_for_selector(sel, state='visible', timeout=2000)
            page.click(sel)
            # clear it first if needed, but usually it's empty or selects all on click
            page.fill(sel, name)
            page.keyboard.press("Enter")
            found_search = True
            # Wait for chat to load
            page.wait_for_timeout(1500) 
            break
        except Exception:
            continue
            
    if not found_search:
        print("Error: see search box not found; cannot select contact by name.")
        return False

    # wait for message box and send
    # Reuse the same logic as send_by_phone basically
    msg_selectors = [
        'div[contenteditable="true"][data-tab]',
        'div[contenteditable="true"]',
        'div[role="textbox"]'
    ]
    
    for ms in msg_selectors:
        try:
            page.wait_for_selector(ms, state='visible', timeout=3000)
            page.click(ms)
            try:
                page.focus(ms)
            except Exception:
                pass
            page.keyboard.type(message)
            if dry_run:
                return True
            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)
            return True
        except Exception:
            continue
    print("Error: message box not found; message not sent.")
    return False


def ensure_logged_in(page, timeout=60):
    page.goto("https://web.whatsapp.com")
    print("If not logged in, please scan the QR code in the opened browser window.")
    try:
        # wait until chat/search UI appears (logged in)
        page.wait_for_selector('div[title="Search input textbox"], div[aria-label="Chat list"], div[role="textbox"]', timeout=timeout*1000)
        return True
    except Exception:
        print("Warning: login not detected after waiting.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Send WhatsApp messages via WhatsApp Web (needs manual QR scan once).")
    parser.add_argument('--phone', help='Phone number in international format, e.g. 15551234567')
    parser.add_argument('--name', help='Contact name as it appears in WhatsApp')
    parser.add_argument('--message', required=True, help='Message text to send')
    parser.add_argument('--repeat', type=int, default=1, help='How many times to send the message')
    parser.add_argument('--delay', type=float, default=1.0, help='Seconds between repeated messages')
    parser.add_argument('--profile-dir', default='./playwright_userdata', help='Directory to store browser profile (keep you logged in)')
    parser.add_argument('--browser-exe', help='Path to Chrome/Edge executable to use for Playwright (optional)')
    parser.add_argument('--browser-lnk', help='Path to a .lnk shortcut pointing to the browser to use (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Open chat and fill message but do not press Enter / send')
    args = parser.parse_args()

    if not args.phone and not args.name:
        print('Provide either --phone or --name to choose the recipient.')
        return

    os.makedirs(args.profile_dir, exist_ok=True)
    # resolve browser executable if provided
    browser_launch_kwargs = {}
    browser_exe = None
    if getattr(args, 'browser_exe', None):
        browser_exe = args.browser_exe
    elif getattr(args, 'browser_lnk', None):
        # try to resolve .lnk to its target on Windows
        lnk = args.browser_lnk
        try:
            from win32com.client import Dispatch
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(lnk)
            target = shortcut.Targetpath
            if target:
                browser_exe = target
        except Exception as e:
            print('Warning: could not resolve .lnk file to executable:', e)

    if browser_exe:
        browser_launch_kwargs['executable_path'] = browser_exe

    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(user_data_dir=args.profile_dir, headless=False, **browser_launch_kwargs)
        page = browser.new_page()
        logged = ensure_logged_in(page)
        if not logged:
            input('Press Enter after you finish scanning the QR and WhatsApp Web is loaded...')

        success = False
        for i in range(args.repeat):
            if args.phone:
                success = send_by_phone(page, args.phone, args.message, dry_run=getattr(args, 'dry_run', False))
            else:
                success = send_by_name(page, args.name, args.message, dry_run=getattr(args, 'dry_run', False))
            if not success:
                print('Failed to send message on attempt', i+1)
            else:
                print('Message sent (attempt', i+1, ')')
            if i < args.repeat - 1:
                time.sleep(args.delay)

        print('Done. Keep the --profile-dir to stay logged in for future runs.')
        # give user a moment to verify before closing
        try:
            page.wait_for_timeout(1000)
        except Exception:
            pass
        try:
            browser.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
