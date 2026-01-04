import speech_recognition as sr
import pyttsx3
import sys
import os
import time
import re
import difflib

# Import existing modules
import contacts_manager
import send_whatsapp_auto

# Initialize TTS
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Try to find a good english voice
for v in voices:
    if "english" in v.name.lower():
        engine.setProperty('voice', v.id)
        break
engine.setProperty('rate', 160) # Speed

def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

import winsound

def listen(r, source, timeout_dur=5):
    # Visual and Auditory cue that mic is ready
    print(f"Listening... (Threshold: {r.energy_threshold})")
    winsound.Beep(500, 200) # Low freq, short beep
    
    try:
        # Increased phrase_time_limit to allow longer pauses/sentences
        audio = r.listen(source, timeout=timeout_dur, phrase_time_limit=15)
        text = r.recognize_google(audio)
        print(f"You said: {text}")
        return text.lower()
    except sr.WaitTimeoutError:
        print("Timeout (silence)")
        return ""
    except sr.UnknownValueError:
        print("Could not understand audio")
        return ""
    except sr.RequestError:
        print("Network error")
        return ""

def parse_contact_from_command(command):
    # Expanded regex to handle "message to", "message tu", "send to" etc.
    # command is already lowercased in listen()
    
    # Remove common start phrases to simplify parsing
    command = command.replace("send a message", "message")
    command = command.replace("send message", "message")
    
    # Regex to capture name. 
    # specific handling for 'tu' which often appears instead of 'to' in Indian English accents
    match = re.search(r'(?:to|tell|msg|message)\s+(?:to\s+|tu\s+)?(\w+(?:\s+\w+)*)', command)
    if match:
        possible_name = match.group(1).strip()
        # unwanted stopwords check
        if possible_name.startswith("to "):
             possible_name = possible_name[3:]
        if possible_name.startswith("tu "):
             possible_name = possible_name[3:]
             
        return possible_name
    return None

def normalize_name(name):
    # Fuzzy match helper using difflib
    contacts = contacts_manager.load_contacts()
    all_names = list(contacts.keys())
    
    # Sanity check: if name is too long (> 4 words), it's probably not a name
    if len(name.split()) > 4:
        return None
    
    # 1. Exact match (case insensitive)
    for c in all_names:
        if c.lower() == name.lower():
            return c
            
    # 2. Contains match
    for c in all_names:
        if name.lower() in c.lower():
            return c
            
    # 3. Fuzzy match (get closest matches)
    # cutoff=0.6 means 60% similarity required
    matches = difflib.get_close_matches(name, all_names, n=1, cutoff=0.6)
    if matches:
        return matches[0]
            
    return None

def main():
    # Setup microphone and ambient noise once
    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Adjusting for ambient noise... ensure silence for 1 second.")
        r.adjust_for_ambient_noise(source, duration=1.0)
        # Disable dynamic adjustment to prevent threshold drifting to 0
        r.dynamic_energy_threshold = False
        print(f"Threshold set to: {r.energy_threshold}")
    
    speak("WhatsApp Voice Assistant Ready. Say 'Send message to [Name]'")
    
    while True:
        # Pass pre-initialized recognizer and source
        with mic as source:
             command = listen(r, source, timeout_dur=10)
             
        if not command:
            continue
            
        if "exit" in command or "stop" in command or "quit" in command:
            speak("Goodbye.")
            break
            
        if "send" in command or "message" in command:
            target_name = parse_contact_from_command(command)
            
            # Name resolution loop
            while True:
                if not target_name:
                    speak("Who do you want to send the message to?")
                    with mic as source:
                        target_name = listen(r, source, timeout_dur=8)
                    if not target_name:
                         break 
                
                resolved_name = normalize_name(target_name)
                if not resolved_name:
                    if len(target_name.split()) > 4:
                         speak("That sounds like a message, not a name. Please say just the contact name.")
                    else:
                         speak(f"I could not find contact {target_name}. Please say the name again.")
                    
                    with mic as source:
                        target_name = listen(r, source, timeout_dur=8)
                    if not target_name:
                        break
                    continue
                
                break
            
            if not resolved_name:
                continue

            phone = contacts_manager.get_phone_by_name(resolved_name)
            speak(f"Found contact {resolved_name}. What is the message?")
            
            content = ""
            for attempt in range(3):
                with mic as source:
                    content = listen(r, source, timeout_dur=10)
                if content:
                    break
                else:
                    if attempt < 2:
                        speak("I didn't hear anything. Please say the message again.")
            
            if not content:
                speak("Timed out waiting for message. Cancelling.")
                continue
                
            speak(f"Ready to send to {resolved_name}. Message is: {content}. Say yes to send.")
            
            confirm = ""
            for attempt in range(3):
                with mic as source:
                    confirm = listen(r, source, timeout_dur=8)
                if confirm:
                     break
                elif attempt < 2:
                     speak("I didn't hear you. Say Yes/Send to confirm, or No to cancel.")
            
            if confirm and ("yes" in confirm or "send" in confirm or "okay" in confirm):
                speak("Sending message now...")
                
                try:
                    # Optimization: Use direct module calls instead of subprocess
                    # This avoids python startup overhead
                    if phone:
                        print(f"Smart Send to {resolved_name} ({phone})")
                        from urllib.parse import quote
                        import send_whatsapp_desktop
                        
                        # 1. Open URL
                        url = f'whatsapp://send?phone={phone}&text={quote(content)}'
                        os.startfile(url)
                        
                        # 2. Key injection
                        # send_message_via_url_mode waits internally
                        if send_whatsapp_desktop.send_message_via_url_mode():
                            speak("Message sent.")
                        else:
                            speak("Mechanism reported failure.")
                    else:
                        # Fallback to search mode if no phone number (less likely here as we resolve name)
                        import send_whatsapp_desktop
                        if send_whatsapp_desktop.send_message_desktop(resolved_name, content):
                            speak("Message sent.")
                        else:
                            speak("Could not send message.")

                except Exception as e:
                    print(f"Error: {e}")
                    speak("Failed to execute sending command.")
            else:
                speak("Cancelled.")
        
        else:
            print("Command ignored.")

if __name__ == "__main__":
    main()
