# Luna Assistant - Termux Setup Guide

## Quick Setup (5 minutes)

### Step 1: Install Termux
1. Download Termux from [F-Droid](https://f-droid.org/packages/com.termux/) or Google Play Store
2. Open Termux and grant necessary permissions

### Step 2: Update and Install Packages
```bash
# Update package list
pkg update && pkg upgrade

# Install required packages
pkg install python python-pip git espeak portaudio pulseaudio ffmpeg sox
```

### Step 3: Install Python Dependencies
```bash
# Install required Python packages
pip install SpeechRecognition pyaudio pyttsx3 requests pydub playsound
```

### Step 4: Set Up Storage Access
```bash
# Grant storage permission
termux-setup-storage

# Grant microphone permission
termux-microphone-record
```

### Step 5: Transfer Luna to Your Phone

#### Option A: USB/ADB (Recommended)
```bash
# On your computer, connect phone via USB
adb push Luna_termux.py /storage/emulated/0/Download/
```

#### Option B: Cloud Storage
1. Upload `Luna_termux.py` to Google Drive/Dropbox
2. In Termux, download it:
```bash
wget "YOUR_CLOUD_LINK/Luna_termux.py"
```

#### Option C: Direct Copy/Paste
1. Copy the content of `Luna_termux.py`
2. In Termux:
```bash
nano Luna_termux.py
# Paste content and save (Ctrl+X, Y, Enter)
```

### Step 6: Run Luna
```bash
# Navigate to where you saved the file
cd /storage/emulated/0/Download/

# Run Luna
python Luna_termux.py
```

---

## Optional: Install Ollama for AI Responses

### Step 1: Install Ollama
```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve
```

### Step 2: Pull a Model
```bash
# In another terminal or after starting ollama serve
ollama pull mistral
```

### Step 3: Test Ollama
```bash
# Test if Ollama is working
ollama run mistral "Hello, how are you?"
```

---

## Troubleshooting

### Audio Issues
```bash
# Start pulseaudio
pulseaudio --start

# Check audio devices
pactl list short sources
```

### Microphone Issues
```bash
# Grant microphone permission
termux-microphone-record

# Test microphone
termux-microphone-record -f test.wav -l 5
```

### Python Path Issues
```bash
# Add Python to PATH
export PATH=$PATH:$HOME/.local/bin
```

### Package Installation Issues
```bash
# Try installing packages one by one
pip install SpeechRecognition
pip install pyaudio
pip install pyttsx3
pip install requests
```

### Permission Issues
```bash
# Make file executable
chmod +x Luna_termux.py

# Check file permissions
ls -la Luna_termux.py
```

---

## Features Available on Termux

✅ **Voice Commands** - "Hey Luna" wake phrase  
✅ **Text Input** - Fallback when voice fails  
✅ **AI Responses** - With Ollama integration  
✅ **Web Browsing** - Open websites  
✅ **Web Search** - Google search  
✅ **Time & Date** - Current time and date  
✅ **Reminders** - Set time-based reminders  
✅ **Alarms** - Set alarms  
✅ **Custom Commands** - Add your own commands  
✅ **Android Features** - Calls, messages, WhatsApp  

---

## Usage Examples

### Basic Commands
```bash
# Wake Luna
"Hey Luna"

# Ask for time
"What time is it?"

# Ask for date
"What's the date?"

# Open websites
"Open YouTube"
"Open Google"
```

### AI Chat
```bash
# Ask questions (requires Ollama)
"What is a black hole?"
"How does photosynthesis work?"
"Tell me a joke"
```

### Android Features
```bash
# Make calls
"Call 1234567890"

# Send messages
"Message John"

# WhatsApp
"Send WhatsApp message"

# Play music
"Play music"
```

### Reminders & Alarms
```bash
# Set reminders
"Remind me to take medicine"

# Set alarms
"Set alarm for 07:30"
```

---

## Tips for Better Performance

1. **Use headphones** for better voice recognition
2. **Speak clearly** and at normal volume
3. **Use text input** in noisy environments
4. **Keep Termux in background** for reminders
5. **Use "help"** command to see all features

---

## File Structure
```
/storage/emulated/0/Download/
├── Luna_termux.py          # Main Luna file
├── luna_memory.json        # Luna's memory (auto-created)
└── termux_setup.md         # This guide
```

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Make sure all packages are installed correctly
3. Verify microphone permissions are granted
4. Try running with text input if voice fails

**Luna is now ready to use on your phone!** 🚀 