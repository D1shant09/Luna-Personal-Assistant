import os
import sys
import json
import datetime
import webbrowser
import platform
import subprocess
import speech_recognition as sr
import threading
import time
import socket
import requests

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from gtts import gTTS
    from playsound import playsound
    import tempfile
except ImportError:
    gTTS = None
    playsound = None

# Termux/Android specific settings
IS_ANDROID = "ANDROID_ROOT" in os.environ
IS_TERMUX = os.path.exists("/data/data/com.termux")
IS_WINDOWS = platform.system() == "Windows"

DATA_FILE = "luna_memory.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({"reminders": [], "alarms": [], "custom_commands": {}}, f)

try:
    with open(DATA_FILE, 'r') as f:
        MEMORY = json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
    MEMORY = {"reminders": [], "alarms": [], "custom_commands": {}}

class Luna:
    def __init__(self, use_realistic_voice=False):
        self.user_name = "Aizard"
        self.recognizer = sr.Recognizer()
        
        # Termux-optimized settings
        if IS_TERMUX:
            self.recognizer.energy_threshold = 4000  # Higher threshold for mobile
            self.recognizer.pause_threshold = 0.8    # Longer pause for mobile
            self.recognizer.dynamic_energy_threshold = True
        else:
            self.recognizer.energy_threshold = 3000
            self.recognizer.pause_threshold = 0.5
            
        self.use_realistic_voice = use_realistic_voice and gTTS is not None and playsound is not None
        self.engine = None
        
        # Initialize voice engine
        if not self.use_realistic_voice and pyttsx3:
            try:
                self.engine = pyttsx3.init()
                voices = self.engine.getProperty('voices')
                
                if voices:
                    # Handle different voice formats
                    if hasattr(voices, '__iter__') and len(voices) > 0:
                        for voice in voices:
                            if hasattr(voice, 'id') and hasattr(voice, 'name'):
                                if 'zira' in voice.id.lower() or 'female' in voice.name.lower():
                                    self.engine.setProperty('voice', voice.id)
                                    break
                    else:
                        # Single voice object
                        if hasattr(voices, 'id'):
                            self.engine.setProperty('voice', voices.id)
                
                self.engine.setProperty('rate', 150)
                self.engine.setProperty('volume', 0.9)
            except Exception as e:
                print(f"Voice engine initialization error: {e}")
                self.engine = None
        
        self.websites = {
            "youtube": "https://youtube.com",
            "google": "https://google.com",
            "github": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
            "reddit": "https://reddit.com",
            "wikipedia": "https://wikipedia.org"
        }
        self.reminder_thread = threading.Thread(target=self.check_reminders, daemon=True)
        self.reminder_thread.start()

    def is_online(self):
        try:
            socket.create_connection(("1.1.1.1", 80), timeout=3)
            return True
        except OSError:
            return False

    def save_memory(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(MEMORY, f, indent=4)
        except Exception as e:
            print(f"Error saving memory: {e}")

    def speak(self, text):
        print(f"Luna: {text}")
        try:
            if self.use_realistic_voice and gTTS and playsound:
                tts = gTTS(text=text, lang='en')
                with tempfile.NamedTemporaryFile(delete=True, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    playsound(fp.name)
            elif self.engine:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as voice_error:
                    # Try to reinitialize the engine
                    try:
                        self.engine = pyttsx3.init()
                        self.engine.setProperty('rate', 150)
                        self.engine.setProperty('volume', 0.9)
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except Exception as reinit_error:
                        print(f"Voice output error: {reinit_error}")
            else:
                # Try to initialize voice engine again
                if pyttsx3 and not self.engine:
                    try:
                        self.engine = pyttsx3.init()
                        self.engine.setProperty('rate', 150)
                        self.engine.setProperty('volume', 0.9)
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except Exception as e:
                        print(f"Voice engine error: {e}")
        except Exception as e:
            print(f"Voice error: {e}")

    def listen(self, prompt=None):
        try:
            with sr.Microphone() as source:
                if prompt:
                    self.speak(prompt)
                print("Listening...")
                
                # Termux-optimized noise adjustment
                if IS_TERMUX:
                    self.recognizer.adjust_for_ambient_noise(source, duration=2)
                else:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            try:
                command = self.recognizer.recognize_google(audio)
                return command.lower()
            except sr.UnknownValueError:
                print("Could not understand audio")
                # Fallback to text input
                user_input = input("[Type your command]: ")
                if user_input.strip():
                    return user_input.strip().lower()
                return None
            except sr.RequestError as e:
                print(f"Could not request results: {e}")
                user_input = input("[Type your command]: ")
                if user_input.strip():
                    return user_input.strip().lower()
                return None
        except Exception as e:
            print(f"Listening error: {e}")
            user_input = input("[Type your command]: ")
            if user_input.strip():
                return user_input.strip().lower()
            return None

    def get_fallback_response(self, query):
        query_lower = query.lower()
        fallback_responses = {
            "black hole": "A black hole is a region of space where gravity is so strong that nothing, not even light, can escape from it. They form when massive stars collapse at the end of their life cycle.",
            "what is a black hole": "A black hole is a region of space where gravity is so strong that nothing, not even light, can escape from it. They form when massive stars collapse at the end of their life cycle.",
            "what is the black hole": "A black hole is a region of space where gravity is so strong that nothing, not even light, can escape from it. They form when massive stars collapse at the end of their life cycle.",
            "what is": "I can help you with many topics. Try asking about specific things like 'What is a black hole?' or 'What is artificial intelligence?'",
            "how": "I can help you with many how-to questions. Try asking something specific like 'How does photosynthesis work?'",
            "why": "I can help explain many things. Try asking something specific like 'Why is the sky blue?'",
            "who": "I can help you learn about people and historical figures. Try asking something specific like 'Who was Albert Einstein?'",
            "when": "I can help you with dates and timelines. Try asking something specific like 'When was the first moon landing?'",
            "where": "I can help you with locations and geography. Try asking something specific like 'Where is Mount Everest?'"
        }
        for key, response in fallback_responses.items():
            if key in query_lower:
                return response
        return "I'm currently offline, but I can help you with basic questions. Try asking about time, date, opening websites, or setting reminders. For complex questions, make sure Ollama is running."

    def chat_with_gpt(self, query):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": query,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response")
                if answer:
                    return answer.strip()
                else:
                    return "I received an empty response from the local AI model."
            else:
                return self.get_fallback_response(query)
        except Exception as e:
            return self.get_fallback_response(query)

    def open_website(self, site):
        url = self.websites.get(site, None)
        if url:
            try:
                if IS_ANDROID:
                    os.system(f"termux-open-url {url}")
                else:
                    try:
                        webbrowser.open(url)
                    except Exception as browser_error:
                        if IS_WINDOWS:
                            os.system(f"start {url}")
                        else:
                            os.system(f"xdg-open {url}")
            except Exception as e:
                self.speak(f"Sorry, I couldn't open {site}. Please try again.")
        else:
            self.speak(f"I don't know how to open {site}")

    def search_web(self, query):
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            if IS_ANDROID:
                os.system(f"termux-open-url {url}")
            else:
                webbrowser.open(url)
        except Exception as e:
            print(f"Error searching web: {e}")

    def get_time(self):
        return datetime.datetime.now().strftime("%I:%M %p")

    def get_date(self):
        return datetime.datetime.now().strftime("%A, %B %d, %Y")

    def execute_android(self, command):
        try:
            if "call" in command:
                number = ''.join(filter(str.isdigit, command))
                if number:
                    os.system(f"termux-telephony-call {number}")
            elif "message" in command:
                self.speak("Who should I message?")
                recipient = self.listen()
                if recipient:
                    self.speak("What should I say?")
                    text = self.listen()
                    if text:
                        os.system(f"termux-sms-send -n {recipient} '{text}'")
            elif "whatsapp" in command:
                self.speak("What should I send on WhatsApp?")
                msg = self.listen()
                if msg:
                    os.system(f"termux-open-url https://wa.me/?text={msg}")
            elif "music" in command:
                os.system("termux-media-player play /sdcard/Music")
        except Exception as e:
            print(f"Android command error: {e}")

    def set_reminder(self, text):
        try:
            self.speak("What time should I remind you? Format: HH:MM")
            time_input = self.listen()
            if time_input and len(time_input) == 5 and ':' in time_input:
                MEMORY["reminders"].append({"text": text, "time": time_input})
                self.save_memory()
                self.speak(f"Reminder set for {time_input}")
            else:
                self.speak("Invalid time format. Please use HH:MM")
        except Exception as e:
            print(f"Reminder error: {e}")

    def set_alarm(self, time_str):
        try:
            if len(time_str) == 5 and ':' in time_str:
                MEMORY["alarms"].append(time_str)
                self.save_memory()
                self.speak(f"Alarm set for {time_str}")
            else:
                self.speak("Invalid time format. Please use HH:MM")
        except Exception as e:
            print(f"Alarm error: {e}")

    def check_reminders(self):
        while True:
            try:
                now = datetime.datetime.now().strftime("%H:%M")
                for reminder in MEMORY["reminders"][:]:
                    if reminder["time"] == now:
                        self.speak(f"Reminder: {reminder['text']}")
                        MEMORY["reminders"].remove(reminder)
                        self.save_memory()
                if now in MEMORY["alarms"]:
                    self.speak("Alarm ringing!")
                    MEMORY["alarms"].remove(now)
                    self.save_memory()
                time.sleep(60)
            except Exception as e:
                print(f"Reminder check error: {e}")
                time.sleep(60)

    def execute(self, command):
        if not command:
            return
        try:
            if "time" in command:
                self.speak(f"The time is {self.get_time()}")
            elif "date" in command:
                self.speak(f"Today is {self.get_date()}")
            elif "open" in command:
                website_found = False
                for key in self.websites:
                    if key in command:
                        self.speak(f"Opening {key}")
                        self.open_website(key)
                        website_found = True
                        break
                if not website_found:
                    if IS_ANDROID:
                        self.execute_android(command)
                    else:
                        self.speak("Which website would you like me to open? I can open YouTube, Google, GitHub, Stack Overflow, Reddit, or Wikipedia.")
            elif "search" in command or "google" in command:
                query = command.replace("search", "").replace("google", "").strip()
                if query:
                    self.speak(f"Searching for {query}")
                    self.search_web(query)
                else:
                    self.speak("What would you like me to search for?")
            elif any(kw in command for kw in ["call", "message", "whatsapp", "play music"]):
                if IS_ANDROID:
                    self.execute_android(command)
                else:
                    self.speak("This feature is only available on Android")
            elif "remind me" in command:
                reminder_text = command.replace("remind me to", "").strip()
                if reminder_text:
                    self.set_reminder(reminder_text)
                else:
                    self.speak("What should I remind you about?")
            elif "set alarm" in command:
                alarm_time = command.replace("set alarm for", "").strip()
                if alarm_time:
                    self.set_alarm(alarm_time)
                else:
                    self.speak("What time should I set the alarm for?")
            elif command in MEMORY["custom_commands"]:
                self.speak(MEMORY["custom_commands"][command])
            elif command.startswith("add command"):
                parts = command.replace("add command", "").strip().split(" say ")
                if len(parts) == 2:
                    MEMORY["custom_commands"][parts[0].strip()] = parts[1].strip()
                    self.save_memory()
                    self.speak(f"Custom command '{parts[0]}' added.")
            elif "help" in command or "what can you do" in command:
                help_text = """I can help you with:
• Opening websites: YouTube, Google, GitHub, Stack Overflow, Reddit, Wikipedia
• Web search: "Search for [topic]" or "Google [topic]"
• Time and date: "What time is it?" or "What's the date?"
• Reminders: "Remind me to [task]"
• Alarms: "Set alarm for [time]"
• Custom commands: "Add command [trigger] say [response]"
• Android features: Call, message, WhatsApp, play music
• Exit: "Goodbye", "Exit", or "Stop"
• AI chat: Ask me anything (requires Ollama running)"""
                self.speak(help_text)
            elif any(x in command for x in ["bye", "exit", "stop", "goodbye"]):
                self.speak("Goodbye! Shutting down Luna.")
                sys.exit(0)
            elif self.is_online():
                response = self.chat_with_gpt(command)
                self.speak(response)
            else:
                self.speak("I'm not sure how to help with that. Try saying 'help' for available commands.")
        except Exception as e:
            print(f"Command execution error: {e}")
            self.speak("Sorry, there was an error processing your command.")

def main():
    try:
        print("🧠 Luna Assistant - Termux/Android Mode")
        print("=" * 40)
        if IS_TERMUX:
            print("Running in Termux environment")
        elif IS_ANDROID:
            print("Running in Android environment")
        else:
            print("Running in desktop environment")
        
        assistant = Luna(use_realistic_voice=False)
        assistant.speak("Luna is ready. Say 'Hey Luna' to wake me up.")
        
        while True:
            try:
                wake = assistant.listen()
                if wake and "hey luna" in wake:
                    assistant.speak("Yes, I'm here.")
                    command = assistant.listen("What can I do for you?")
                    if command:
                        assistant.execute(command)
                    assistant.speak("Going back to sleep.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                continue
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 