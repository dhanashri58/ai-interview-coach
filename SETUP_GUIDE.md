🚀 AI Interview Coach — Complete Setup Guide

## 1. 📋 Prerequisites — What You Need Before Starting

Before starting the setup process, ensure you have the following ready on your computer:

- **Python 3.8 or higher** — Check your version by typing `python --version` in your terminal.
- **Git installed** — Check by typing `git --version` in your terminal.
- **A webcam and microphone** — Required for the video and audio portions of the interview.
- **A Google account** — Required to get a free Gemini API key for AI features.
- **Internet connection** — Required to download packages and access the AI APIs.
- *Windows, Mac, and Linux* are all fully supported!

---

## 2. 📥 Step 1 — Clone The Project

Cloning simply means downloading an exact copy of the code repository from the internet onto your local computer so you can run it.

Open your terminal or command prompt and run:
```bash
git clone https://github.com/your-username/ai-interview-coach.git
cd ai-interview-coach
```

---

## 3. 🐍 Step 2 — Create a Virtual Environment

A virtual environment is an isolated, invisible box inside your project folder where you install Python packages, ensuring they never clash or interfere with other projects on your computer.

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

*💡 You will know this worked successfully if you see `(venv)` appearing at the very start of your terminal line.*

---

## 4. 📦 Step 3 — Install Dependencies

This command reads the project's shopping list of external code and installs all the required libraries automatically. *Note: this might take 2-3 minutes the first time you run it.*

```bash
pip install -r requirements.txt
```

**Here is exactly what gets installed and why we need it:**
- `streamlit==1.28.0` — The core web framework that constructs and draws the entire user interface.
- `openai==0.28.0` — Kept for legacy fallback compatibility.
- `python-dotenv==1.0.0` — Reads your hidden `.env` file to load your API keys securely without exposing them.
- `pandas==2.0.3` — Data manipulation library responsible for structuring your final analytics.
- `plotly==5.17.0` — Draws the beautiful, interactive progress charts on the final report card.
- `speechrecognition==3.10.0` — Processes the raw audio from your microphone and converts it into readable text.
- `pyttsx3==2.90` — An offline, desktop-based text-to-speech fallback engine.
- `PyAudio==0.2.13` — Connects Python directly to your physical microphone hardware.
- `google-generativeai==0.3.0` — The official Google library to connect to the Gemini API for smart, generative insights.
- `streamlit-webrtc==0.45.0` — A legacy component utilized for camera streaming support.
- `audio-recorder-streamlit==0.0.8` — The visual microphone recording button plugin for the Streamlit UI.
- `gTTS==2.5.4` — Google Text-to-Speech library serving as the secondary voice fallback engine.
- `edge-tts` — Microsoft Neural Text-to-Speech library that generates the highly realistic, human-sounding AI voices.

---

## 5. 🔑 Step 4 — Get Your Gemini API Key (Free)

To enable the powerful "Instant Coaching Tip" and personalized greetings features, you need a free Google Gemini key.

1. Open your browser and go to: `https://aistudio.google.com`
2. Sign in with any active Google account.
3. Click on **"Get API Key"** in the top left menu navigation.
4. Click the blue **"Create API Key"** button.
5. Select **"Create API key in new project"**.
6. Your new API key will appear in a popup box — it generally looks like: `AIzaSy...........`
7. Copy the entire string — you will need to paste it in the very next step.

> ⚠️ IMPORTANT: Never share your API key publicly.  
> Never paste it in a chat, email, or commit it to GitHub.  
> This key is like a password — treat it that way.

**Free Tier Limits:**
- **Model:** `gemini-3.1-flash-lite`
- 15 requests per minute
- 500 requests per day
- *No credit card is required to claim this key.*

---

## 6. 🔐 Step 5 — Create Your .env File

A `.env` (dot-env) file is a hidden configuration file that stores your secret keys locally on your computer. It is listed in `.gitignore` so it never gets uploaded to GitHub — keeping your personal API keys completely private.

Create a new plain text file called exactly `.env` (don't forget the dot at the beginning!) in the root folder of your project.

Your folder structure should look like this:
```text
ai-interview-coach/
├── .env          ← your new file goes here
├── app.py
├── requirements.txt
└── ...
```

Copy and paste the following structure into your new `.env` file, making sure to replace the placeholder `your_..._here` values with your real keys:

```env
# AI Interview Coach — Environment Variables
# Never commit this file to GitHub

# API Keys for AI Services
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# App Configuration
APP_NAME=AI Interview Coach
APP_VERSION=1.0.0
DEBUG=True

# Database (if using)
DATABASE_URL=sqlite:///interview_coach.db

# Voice Settings
ENABLE_VOICE=True
DEFAULT_VOICE_RATE=150
DEFAULT_VOICE_VOLUME=0.8
```

---

## 7. ✅ Step 6 — Verify Your Setup

Before launching the full web app, run this quick check command to verify your Python environment has installed the complex media libraries correctly:

```bash
python -c "import streamlit; import edge_tts; import speech_recognition; print('All dependencies OK')"
```
*(If it prints "All dependencies OK" without errors, you are ready to proceed!)*

---

## 8. 🚀 Step 7 — Run The Application

You are now ready to launch the virtual interview room!

**For Windows (shortcut):**
```bash
.\run.bat
```

**For Any Operating System (manual):**
```bash
streamlit run app.py
```

The app will automatically open a new tab in your default browser at `http://localhost:8501`. **Be sure to click "Allow" when the browser asks for permission to use your Camera and Microphone!**

---

## 9. 🎯 Step 8 — First Launch Checklist

Once the UI loads, follow this quick checklist to ensure everything is working:

- [ ] Look at the left sidebar and open the **"👤 Your Profile"** expander. Fill in your Name, Email, and Target Role, then click "SAVE PROFILE".
- [ ] Open the **"🎙️ Voice Settings"** expander. Select a voice ("Jenny" or "Guy") and click the **"🔊 Test Voice"** button. You should hear the AI speak loudly and clearly.
- [ ] Open the **"⚙️ Interview Settings"** expander and ensure you can toggle "Use Pre-Planned Syllabus" and "Enable AI-Enhanced Mode" checkboxes.
- [ ] In the main central view, verify that you can see your live webcam feed rendered cleanly in the dark "Live Camera" card.
- [ ] Verify that the AI Coach Avatar is visible next to your camera feed.
- [ ] Click the large **"🚀 START YOUR INTERVIEW"** button to verify the system transitions into the intro stage.

---

## 10. 🤖 Step 9 — Enable AI Enhanced Mode

To unlock personalized tips and dynamically generated voice lines:

1. Double-check that your `.env` file has the `GEMINI_API_KEY` correctly filled in and saved.
2. Find the **"⚙️ Interview Settings"** expander in the sidebar.
3. Turn **ON** the `⚡ Enable AI-Enhanced Mode (Gemini)` toggle.
4. Start a new interview session.
5. Watch your terminal console while the app is running; you should see success logs confirming that the Gemini API is answering your requests!

---

## 11. ❓ Troubleshooting — Common Problems

**Camera not showing**
- *Cause:* Browser permission was denied or a physical webcam cover is engaged.
- *Fix:* Click the little "Camera/Lock" icon in the far left of your browser's URL address bar. Ensure the Camera dropdown is set to "Allow". Refresh the page.

**Microphone not working**
- *Cause:* The `audio-recorder-streamlit` component failed to attach to the correct audio interface or the mic is globally muted.
- *Fix:* Check your system sound settings and ensure the correct input device is selected. Grant microphone permissions in the browser URL bar like you did for the camera, and refresh.

**No voice / TTS silent**
- *Cause:* Volume is low, or the computer lacks an active internet connection to download the `edge-tts` Microsoft AI voices.
- *Fix:* Verify your PC speakers are on and not muted. Ensure you are connected to the internet. If it continues to fail silently, check the terminal for any `edge-tts` timeout errors. 

**Gemini API not working**
- *Cause:* The `GEMINI_API_KEY` is invalid, expired, or the `.env` file was not placed in the exact right directory.
- *Fix:* Verify the `.env` file is named exactly `.env` (not `env.txt`). Restart the app completely by pressing `CTRL+C` in the terminal and running `streamlit run app.py` again so it re-reads the secrets file.

**ModuleNotFoundError on startup**
- *Cause:* The libraries were installed in the global computer environment instead of the project's virtual environment.
- *Fix:* Ensure the `(venv)` tag is visibly present in your terminal. If it isn't, re-run `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux), and then run `pip install -r requirements.txt` again.

**App opens but shows blank white screen**
- *Cause:* Streamlit is encountering a silent fatal rendering error, usually caused by a caching conflict or a stuck browser state.
- *Fix:* In your terminal, stop the server with `CTRL+C`. Run `streamlit cache clear`. Open a completely "New Incognito / Private Window" in your browser and go to `localhost:8501`.

---

## 12. 📁 Complete Project Structure Reference

- `.env` — Stores your secret API keys (do not share).
- `.git/` — Version control system folder.
- `.gitignore` — Tells Git which files to ignore (like venv and .env).
- `README.md` — The general overview documentation for the project.
- `SOFTWARE_UNDERSTANDING.md` — Deep technical dive explaining how all algorithms and architectures connect.
- `answer_evaluator.py` — The Forward-Chaining logic engine that grades answers without LLMs.
- `app.py` — The primary Streamlit user interface and application orchestrator.
- `interview_planner_csp.py` — Constraint Satisfaction Algorithm for generating static interview syllabuses.
- `knowledge_base.py` — The core repository of all questions, answers, concepts, and keywords.
- `learning_path_astar.py` — Optimal pathfinding (A* Search) logic to generate the fastest study curriculum.
- `performance_report.py` — Combines scoring analytics into final feedback graphs and summaries.
- `question_selector.py` — Best-First Search heuristic logic to dynamically ask adaptive questions.
- `requirements.txt` — The list of exactly every Python package required to run the project.
- `run.bat` — Simple Windows shortcut to launch the app cleanly.
- `utils.py` — Collection of essential tools for avatar rendering, Voice (Edge-TTS), animation, and Gemini integration.
- `venv/` — Your isolated Python virtual environment housing the installed packages.

---

## 13. 🎓 Course Information

```text
Course:    ML2306 — Artificial Intelligence
Institute: Vishwakarma Institute of Technology, Pune
Board:     Savitribai Phule Pune University
Year:      A.Y. 2025-26

AI Algorithms Implemented:
- Unit II:  Breadth-First Search (Knowledge Base Explorer)
- Unit III: Best-First Search (Question Selection)
- Unit III: A* Search (Learning Path Generation)
- Unit III: Constraint Satisfaction + Backtracking (Interview Planner)
- Unit IV:  Forward Chaining (Answer Evaluation)
- Unit V:   Expert System (Knowledge Base + Inference Engine)
```
