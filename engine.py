import sys
import datetime
import json
import urllib.request
import urllib.parse
import re
import time
import subprocess
import os
import shutil
import webbrowser
import threading

try:
    import pyaudiowpatch as pyaudio
    sys.modules['pyaudio'] = pyaudio
except ImportError:
    pass

try:
    import types
    import packaging.version as p_ver
    distutils_mod = types.ModuleType("distutils")
    version_mod = types.ModuleType("distutils.version")
    version_mod.LooseVersion = p_ver.Version 
    distutils_mod.version = version_mod
    sys.modules["distutils"] = distutils_mod
    sys.modules["distutils.version"] = version_mod
except ImportError:
    import types
    distutils_mod = types.ModuleType("distutils")
    version_mod = types.ModuleType("distutils.version")
    class DummyLooseVersion:
        def __init__(self, vstring): self.vstring = vstring
        def __str__(self): return self.vstring
        def __lt__(self, other): return False
        def __le__(self, other): return True
        def __eq__(self, other): return True
    version_mod.LooseVersion = DummyLooseVersion
    distutils_mod.version = version_mod
    sys.modules["distutils"] = distutils_mod
    sys.modules["distutils.version"] = version_mod

import speech_recognition as sr
import pyttsx3

class WindowsAssistantEngine:
    def __init__(self):
        self.last_intent = None
        self.recognizer = sr.Recognizer()
        self.is_running = True
        self.is_speaking = False 
        self.pause_background_mic = False  
        self.current_city = "Nagpur"
        self.speak_lock = threading.Lock()
        
        self.shopping_list = []
        self.reminders = []
        
        try:
            self.voice_engine = pyttsx3.init()
            self.voice_engine.setProperty('rate', 175)
            voices = self.voice_engine.getProperty('voices')
            if len(voices) > 1:
                self.voice_engine.setProperty('voice', voices[1].id)
        except Exception:
            self.voice_engine = None

        self.auto_detect_location()
        # --- OPTIMIZED AUDIO CORE TRIGGER VALUES ---
        self.recognizer.energy_threshold = 300  # Initial sensitivity baseline
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15  # Adjusts rapidly to room noise
        self.recognizer.dynamic_energy_ratio = 1.3  # Keeps speech threshold close to ambient floor
        self.recognizer.pause_threshold = 0.5  # Snappy cutoff so it doesn't wait too long to parse

        # Dictionary of common system shorthands to normalize conversational variations
        self.alias_matrix = {
            "vs code": "code",
            "vscode": "code",
            "word": "winword",
            "powerpoint": "powerpnt",
            "paint": "mspaint",
            "command prompt": "cmd",
            "terminal": "cmd",
            "browser": "chrome",
            "whatsapp web": "whatsappweb"
        }

    def speak(self, text):
        if self.voice_engine and self.speak_lock.acquire(blocking=False):
            try:
                clean_text = text.replace("•", "").replace("\n", " ")
                self.voice_engine.say(clean_text)
                self.voice_engine.runAndWait()
            except Exception:
                pass
            finally:
                self.speak_lock.release()

    def auto_detect_location(self):
        try:
            url = "http://ip-api.com/json/"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                if data.get("status") == "success":
                    self.current_city = data.get("city", "Nagpur")
        except Exception:
            pass

    # 🎧 RE-ENGINEERED CONTINUOUS STREAM ENGINE
    def monitor_continuous_stream(self, on_listen_callback, on_command_callback):
        import pyaudiowpatch as pyaudio
        p = pyaudio.PyAudio()
        input_device_index = None
        try:
            default_input = p.get_default_input_device_info()
            input_device_index = default_input.get("index")
        except Exception:
            for i in range(p.get_device_count()):
                dev = p.get_device_info_by_index(i)
                if dev.get('maxInputChannels', 0) > 0 and 'loopback' not in dev.get('name', '').lower():
                    input_device_index = i
                    break
        finally:
            p.terminate()

        with sr.Microphone(device_index=input_device_index) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
            
            while self.is_running:
                if self.pause_background_mic:
                    time.sleep(0.2)
                    continue
                try:
                    audio = self.recognizer.listen(source, timeout=1.2, phrase_time_limit=3.5)
                    if self.pause_background_mic:
                        continue
                    
                    phrase = self.recognizer.recognize_google(audio).strip()
                    if len(phrase) > 2:
                        on_listen_callback()
                        on_command_callback(phrase, True)
                        
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception:
                    time.sleep(0.3)

    def recognize_command(self, source, on_command_callback):
        try:
            audio_data = self.recognizer.listen(source, timeout=4, phrase_time_limit=6)
            spoken_command = self.recognizer.recognize_google(audio_data)
            on_command_callback(spoken_command, True)
        except Exception:
            on_command_callback("Command capture timed out or unreadable.", False)

    # 🚀 HIGH-SPEED APPLICATION LAUNCHER (OPTIMIZED)
    # 🚀 HIGH-SPEED APPLICATION LAUNCHER (FINAL FIX)
    def smart_launch_app(self, app_token):
        # Normalize vocabulary aliases down to actual system execution tokens
        executable = self.alias_matrix.get(app_token, app_token)
        executable = executable.replace(".exe", "").replace(".cmd", "").strip()

        native_windows_apps = {
            "calculator": "calc.exe",
            "calc": "calc.exe",
            "notepad": "notepad.exe",
            "paint": "mspaint.exe",
            "mspaint": "mspaint.exe",
            "cmd": "cmd.exe",
            "command prompt": "cmd.exe",
            "taskmgr": "taskmgr.exe",
            "task manager": "taskmgr.exe",
            # Use Windows system URI protocol allocation directly
            "whatsapp": "whatsapp://"
        }

        # 1. Instant execution for native utilities or system protocol links
        if executable in native_windows_apps:
            try:
                target_cmd = native_windows_apps[executable]
                if target_cmd.startswith("whatsapp://"):
                    # Launch directly via OS protocol handling to prevent file manager fallbacks
                    os.startfile(target_cmd)
                else:
                    subprocess.Popen(target_cmd)
                return f"Opening local native {app_token.upper()} desktop application."
            except Exception:
                pass

        # 3. FAST SCAN: Search Windows Start Menu shortcuts (Incredibly quick)
        start_menu_paths = [
            os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
            os.path.join(os.environ.get("AppData", ""), "Microsoft\\Windows\\Start Menu\\Programs")
        ]

        for menu_dir in start_menu_paths:
            if not menu_dir or not os.path.exists(menu_dir):
                continue
            for root, dirs, files in os.walk(menu_dir):
                for file in files:
                    # Match app name against shortcut labels (e.g., "chrome.lnk" or "spotify.lnk")
                    if executable in file.lower():
                        shortcut_path = os.path.join(root, file)
                        try:
                            os.startfile(shortcut_path)
                            return f"Start Menu shortcut found. Launching local {app_token.upper()} client."
                        except Exception:
                            pass

        # 4. RESTRICTED DEEP SCAN: Only check top-level folders (Max depth 2)
        search_dirs = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.environ.get("LocalAppData", "")
        ]
        
        for base_dir in search_dirs:
            if not base_dir or not os.path.exists(base_dir):
                continue
            try:
                # Only check main directories instead of recursive infinite walking
                for top_level_item in os.listdir(base_dir):
                    sub_path = os.path.join(base_dir, top_level_item)
                    if os.path.isdir(sub_path):
                        # Look for target executable directly in the root of its program folder
                        potential_exe = os.path.join(sub_path, f"{executable}.exe")
                        if os.path.exists(potential_exe):
                            subprocess.Popen(f'"{potential_exe}"', shell=True)
                            return f"Local program match isolated. Opening {app_token.upper()} client."
            except Exception:
                continue

        # 5. Final Fallback: Use direct os command execution or search tab
        try:
            subprocess.Popen(f"{executable}.exe")
            return f"Sending direct application start token to Windows for '{app_token}'."
        except Exception:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(app_token)}"
            webbrowser.open_new_tab(search_url)
            return f"Unable to locate local app client for '{app_token}'. Opened browser search frame."

    def fetch_weather(self):
        try:
            sanitized_city = urllib.parse.quote(self.current_city)
            url = f"https://wttr.in/{sanitized_city}?format=j1"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode())
                current = data['current_condition'][0]
                return f"Currently in {self.current_city}: {current['temp_C']}°C and {current['weatherDesc'][0]['value'].lower()}."
        except Exception:
            return f"Unable to fetch weather info right now."

    def fetch_smart_answer(self, user_query):
        try:
            encoded_query = urllib.parse.quote(user_query)
            api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get("AbstractText"):
                    return data["AbstractText"]
                if data.get("Definition"):
                    return data["Definition"]
                if data.get("RelatedTopics") and len(data["RelatedTopics"]) > 0:
                    text_chunk = data["RelatedTopics"][0].get("Text")
                    if text_chunk:
                        return text_chunk
        except Exception:
            pass
        return None

    def execute_intent(self, query):
        query = str(query).strip().lower()
        if not query:
            return "No active instruction token caught."

        if "add " in query and "shopping list" in query:
            item = query.replace("add ", "").replace("to my shopping list", "").replace("to shopping list", "").strip()
            self.shopping_list.append(item.capitalize())
            return f"Added '{item.capitalize()}' to your active shopping list framework."
            
        if "show" in query and "shopping list" in query:
            if not self.shopping_list:
                return "Your shopping list is currently empty."
            return "Active Shopping List:\n" + "\n".join([f"• {i}" for i in self.shopping_list])

        if "clear" in query and "shopping list" in query:
            self.shopping_list.clear()
            return "Shopping list cleared cleanly."

        if "remind me to" in query:
            reminder_text = query.replace("remind me to", "").strip()
            self.reminders.append(reminder_text.capitalize())
            return f"Task logged! I will remind you to: {reminder_text.capitalize()}."

        if "show" in query and "reminders" in query:
            if not self.reminders:
                return "You have no active system reminders set."
            return "Logged System Reminders:\n" + "\n".join([f"• {r}" for r in self.reminders])

        if "traffic" in query or "directions" in query or "map" in query:
            map_url = f"http://googleusercontent.com/maps.google.com/4{urllib.parse.quote(query)}"
            webbrowser.open_new_tab(map_url)
            return f"Opening navigation map overlay variables in your browser."

        if "find nearby" in query or "near me" in query:
            search_url = f"http://googleusercontent.com/maps.google.com/4{urllib.parse.quote(query)}"
            webbrowser.open_new_tab(search_url)
            return f"Scanning geospatial data points for your request. View browser window."

        # DYNAMIC OPEN HOOK
        if query.startswith("open ") or query.startswith("play "):
            target = query.replace("open ", "").replace("play ", "").strip()
            
            if "youtube" in query or query.startswith("play "):
                song_search = target.replace("on youtube", "").replace("youtube", "").strip()
                url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_search)}"
                webbrowser.open_new_tab(url)
                return f"Opening YouTube media stream matrix for '{song_search}' in your browser window."
                
            # Will now accept any spoken target name cleanly!
            return self.smart_launch_app(target)

        if any(w in query for w in ['weather', 'temperature', 'climate']):
            return self.fetch_weather()
            
        if 'time' in query:
            return f"The time in {self.current_city} is {datetime.datetime.now().strftime('%I:%M %p')}."

        if any(w in query for w in ['hello', 'hi', 'hey']):
            return f"Hello! AIRA matrix active. How can I assist you today?"
        
        if "translate" in query or "how do you say" in query:
            trans_url = f"https://translate.google.com/?sl=auto&tl=en&text={urllib.parse.quote(query)}"
            webbrowser.open_new_tab(trans_url)
            return "Opening Google Translation subsystem interface in a new window."

        if any(keyword in query for keyword in ["what is", "who is", "define", "explain", "meaning of"]):
            smart_answer = self.fetch_smart_answer(query)
            if smart_answer:
                return f"[Smart Query Result]: {smart_answer}"

        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open_new_tab(search_url)
        return f"Could not extract a direct info capsule. Launching web matrix engine for '{query}' in a new tab window."