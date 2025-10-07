🐾 AI Desktop Pet

The AI project and the Desktop UI is currently disconnected, this feature will be available soon

An AI-powered desktop pet that lives on your computer, interacts with your actions, and responds intelligently through natural conversation and voice.
This project combines Google’s Gemini 2.5 Flash, GPT-SoVITS voice synthesis, and the Godot 4.4 Mono engine to create a charming and responsive AI companion.

🧠 Features

💬 Conversational AI powered by Gemini 2.5 Flash (via Google API)

🔊 Realistic voice using GPT-SoVITS TTS

🎮 Interactive desktop interface built with Godot Game Engine 4.4 Mono

⚙️ Customizable personality and voice

🖥️ Works directly on your desktop, no browser required (doesn't run fully locally, require internet)

🛠️ Installation
1. Clone the repository
git clone https://github.com/DevPhusion/AI-Chan.git
cd AI-Chan

2. Install dependencies

Create and activate a virtual environment (recommended):

python -m venv venv
source venv/bin/activate     # On Linux/Mac
venv\Scripts\activate        # On Windows


Then install all required libraries:

pip install -r requirements.txt

3. Install GPT-SoVITS

Follow setup instructions here:
👉 GPT-SoVITS GitHub Repository

4. Install Godot Game Engine

Download and install Godot 4.4 Stable (Mono version) from the official site:
👉 https://godotengine.org/download

🔑 Setup

Obtain your Gemini API Key
Get it from Google AI Studio
.

Configure the project
Open main.py and modify:

SYSTEM_PROMPT = "Your custom AI personality prompt"
REF_AUDIO_PATH = "path/to/your/reference_audio.wav"


SYSTEM_PROMPT: Defines how your AI pet behaves and speaks.

REF_AUDIO_PATH: The voice reference file used for TTS generation.

▶️ Running the Project

Open the project in Godot 4.4 Mono.

Press Play ▶️ to start the AI pet.

Your AI pet should appear and begin interacting!


⚙️ File Overview
project_root/

├── __pycache__/                # Compiled Python cache

├── .venv/                      # Virtual environment

├── DesktopUI/                  # Godot UI project files

├── GPT-SoVITS/                 # GPT-SoVITS setup and models

├── functions.json              # Configuration or function mapping for AI behavior

├── main.py                     # Main Python entry point

├── ref_audio.wav               # Reference Audio                

🧩 Customization Tips

Change AI Personality: Edit SYSTEM_PROMPT in main.py.

Voice Customization: Replace or modify REF_AUDIO_PATH with a different voice sample.

Extend Abilities: Modify the Godot UI to add pet interactions (idle animations, click reactions, etc.)

Import your own models: You can import your own models (format: .glb) and apply the toon shaders, outline shaders 

💡 Future Plans
Add runnable .exe release

Connect AI model to Godot Projects

More interactions with AI agent

Better model animation

🧑‍💻 Credits

AI Model: Google Gemini 2.5 Flash

TTS Engine: GPT-SoVITS

Game Engine: Godot 4.4 Mono

Developed by: Phusion
