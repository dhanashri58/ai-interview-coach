"""
AI Interview Coach — Professional Edition v3.0
Main Streamlit Application

Architecture:
  - knowledge_base.py  : Question bank + ideal answers (UNCHANGED)
  - question_selector.py: Best-First heuristic selector (UNCHANGED)
  - answer_evaluator.py : Forward-chaining evaluator (UNCHANGED)
  - performance_report.py: Analytics & learning path (UNCHANGED)
  - utils.py           : Animations, TTS, STT helpers (extended)
  - app.py             : UI orchestration (this file)

Interview Flow (new):
  Stage 0 — Intro      : AI greets candidate by name via TTS
  Stage 1 — Questions  : Ask → Listen → Store (NO per-question feedback)
  Stage 2 — Wrap-up    : AI thanks candidate via TTS
  Stage 3 — Report     : Full evaluation shown after interview ends
"""

# ---------------------------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import json

# Backend logic engines (never modified)
from knowledge_base import KnowledgeBase
from question_selector import QuestionSelector
from answer_evaluator import AnswerEvaluator
from performance_report import PerformanceReport
from interview_planner_csp import ConstraintSatisfactionPlanner


# Utility helpers (TTS, STT, animations)
from utils import (
    get_typing_animation, get_robot_avatar,
    get_difficulty_level, format_feedback,
    text_to_speech_autoplay, speech_to_text,
    get_progress_ring
)

# st.components for embedding native HTML/JS camera (no server relay needed)
import streamlit.components.v1 as components

# Browser microphone recording
try:
    from audio_recorder_streamlit import audio_recorder
    AUDIO_RECORDER_AVAILABLE = True
except ImportError:
    AUDIO_RECORDER_AVAILABLE = False

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Interview Coach — Professional",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

import random

# Human-like AI Conversation constants
TRANSITIONS = [
    "Okay, that's a good point. Let me ask you something else.",
    "Interesting, I like that answer. Moving on.",
    "Right, good. Let's shift gears a bit.",
    "Got it, thank you. Here's my next question for you.",
    "Alright, I appreciate that. Now let me ask you about something different.",
    "That's helpful context. Let me follow up with this.",
    "Good, I'm getting a clearer picture. Next question.",
    "Thank you for that. Let's continue.",
]

ACKNOWLEDGEMENTS = [
    "Mmhm, okay.",
    "Right, I see.",
    "Got it, thank you.",
    "Okay, noted.",
    "Alright.",
    "Sure, that makes sense.",
    "Good, thank you for that.",
]

TIMING = {
    "after_acknowledgement": 0.6,   # pause after "Got it"
    "before_question": 0.8,         # pause before asking next question  
    "after_question_spoken": 0.3,   # brief pause after TTS finishes
    "closing_between_lines": 1.0,   # pause between closing sentences
}

# ---------------------------------------------------------------------------
# GLOBAL CSS — Google Meet–inspired dark interview room + sidebar polish
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Meet header bar ── */
.meet-header {
    background: #202124;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.meet-title { font-size: 1rem; font-weight: 600; color: #e8eaed; }
.meet-meta  { font-size: 0.85rem; color: #9aa0a6; }
.status-dot {
    display: inline-block; width:10px; height:10px;
    border-radius: 50%; margin-right: 6px;
}
.dot-live { background:#34a853; animation: pulse-dot 1.5s infinite; }
.dot-idle { background:#9aa0a6; }
@keyframes pulse-dot {
    0%,100% { opacity:1; transform:scale(1); }
    50% { opacity:.6; transform:scale(1.3); }
}

/* ── Video panels ── */
.panel-ai {
    background: #2d2f31;
    border: 2px solid #3c4043;
    border-radius: 14px;
    padding: 1.25rem;
    text-align: center;
    min-height: 280px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    position: relative;
}
.panel-candidate {
    background: #1a1b1e;
    border: 2px solid #3c4043;
    border-radius: 14px;
    padding: 1.25rem;
    text-align: center;
    min-height: 280px;
    position: relative;
}
.panel-label {
    position: absolute; bottom: 12px; left: 14px;
    background: rgba(0,0,0,0.6);
    color:white; font-size:0.8rem; font-weight:500;
    padding: 3px 10px; border-radius: 20px;
}

/* ── Speaking indicator ── */
.speaking-ring {
    border: 3px solid #34a853;
    border-radius: 50%; padding: 6px;
    animation: speak-pulse 0.8s infinite alternate;
    display: inline-block;
}
@keyframes speak-pulse {
    from { box-shadow: 0 0 4px #34a853; }
    to   { box-shadow: 0 0 18px #34a853; }
}
.listening-badge {
    background: #ea4335; color:white;
    font-size:0.78rem; font-weight:600;
    padding: 4px 14px; border-radius: 20px;
    animation: pulse-dot 1s infinite;
    display: inline-block; margin-top: 6px;
}

/* ── Meet control bar ── */
.control-bar {
    background: #202124;
    border-radius: 14px;
    padding: 0.6rem 1rem;
    display: flex; justify-content: center; gap: 1rem;
    align-items: center;
    margin-top: 1rem;
}

/* ── Question card ── */
.q-card {
    background: linear-gradient(135deg,#1a237e 0%,#283593 100%);
    color: white;
    padding: 1.25rem 1.5rem;
    border-radius: 14px;
    border-left: 5px solid #667eea;
    margin: 0.75rem 0;
    box-shadow: 0 6px 20px rgba(102,126,234,0.25);
}
.q-number { font-size:0.75rem; opacity:0.75; text-transform:uppercase; letter-spacing:0.5px; }
.q-text   { font-size:1.15rem; font-weight:500; line-height:1.6; margin-top:0.4rem; }
.q-topic  { font-size:0.8rem; opacity:0.6; margin-top:0.6rem; }

/* ── Badge styles ── */
.badge {
    display:inline-block; padding:0.3rem 0.9rem; border-radius:9999px;
    font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;
}
.badge-beginner     { background:#fef3c7; color:#92400e; border:1px solid #fbbf24; }
.badge-intermediate { background:#bfdbfe; color:#1e40af; border:1px solid #3b82f6; }
.badge-advanced     { background:#fecaca; color:#991b1b; border:1px solid #ef4444; }
.badge-expert       { background:#d1fae5; color:#065f46; border:1px solid #10b981; }
.badge-needs_practice { background:#fee2e2; color:#991b1b; }

/* ── Metric cards ── */
.metric-card {
    background:white; border-radius:14px; padding:1.25rem;
    text-align:center; box-shadow:0 4px 10px rgba(0,0,0,0.07);
    border-left:4px solid #667eea;
}
.metric-value { font-size:1.9rem; font-weight:700; color:#1e293b; }
.metric-label { font-size:0.8rem; color:#718096; text-transform:uppercase; letter-spacing:0.5px; }

/* ── Professional sidebar header ── */
.sidebar-header {
    color:#1e293b; font-weight:600; margin-bottom:0.4rem;
    padding-bottom:0.4rem; border-bottom:2px solid #667eea;
}

/* ── Feedback box ── */
.feedback-box {
    background:linear-gradient(135deg,#f8fafc 0%,#f1f5f9 100%);
    padding:1.25rem; border-radius:14px; margin:0.75rem 0;
    border:1px solid #e2e8f0;
}

/* ── Score colours ── */
.score-high   { color:#10b981; font-weight:700; font-size:1.1rem; }
.score-medium { color:#f59e0b; font-weight:700; font-size:1.1rem; }
.score-low    { color:#ef4444; font-weight:700; font-size:1.1rem; }

/* ── Welcome hero ── */
.hero-box {
    background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    padding:2.5rem 3rem; border-radius:20px; color:white;
    text-align:center; box-shadow:0 20px 40px rgba(102,126,234,0.3);
    margin: 1rem 0 2rem;
}

/* ── Buttons ── */
.stButton > button {
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    color:white; border:none; border-radius:10px;
    font-weight:600; letter-spacing:0.4px;
    box-shadow:0 4px 8px rgba(102,126,234,0.3);
    transition: transform .2s, box-shadow .2s;
}
.stButton > button:hover {
    transform:translateY(-2px);
    box-shadow:0 8px 16px rgba(102,126,234,0.4);
}

/* ── Progress bar ── */
.stProgress > div > div {
    background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    border-radius:10px; height:9px;
}

/* ── Footer ── */
.footer {
    text-align:center; padding:1.5rem;
    color:#a0aec0; font-size:0.85rem;
    border-top:1px solid #e2e8f0; margin-top:3rem;
}
hr { margin:1.5rem 0; border:0; height:1px;
     background:linear-gradient(135deg,transparent,#667eea,transparent); }
</style>
""", unsafe_allow_html=True)

# Inject typing / bounce / float CSS from utils
st.markdown(get_typing_animation(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE — initialise only once per browser session
# ---------------------------------------------------------------------------
def init_session_state():
    """
    Initialise all session-level variables.
    New variables added for interview-flow stage management:
      interview_stage : 'intro' | 'questions' | 'wrapup' | 'report'
      intro_spoken    : bool — has the greeting TTS been emitted?
      mic_muted       : bool — user has muted their mic
      cam_off         : bool — user has turned camera off
      interview_start_time : datetime — for elapsed timer
    """
    if 'initialized' not in st.session_state:
        st.session_state.initialized        = True
        # ── backend engines ──
        st.session_state.kb                 = KnowledgeBase()
        st.session_state.selector           = QuestionSelector(st.session_state.kb)
        st.session_state.evaluator          = AnswerEvaluator(st.session_state.kb)
        st.session_state.reporter           = PerformanceReport()
        # ── interview state ──
        st.session_state.interview_active   = False
        st.session_state.interview_complete = False
        st.session_state.interview_stage    = 'idle'   # idle/intro/questions/wrapup/report
        st.session_state.intro_spoken       = False
        st.session_state.current_question   = None
        st.session_state.question_history   = []       # IDs of asked questions
        st.session_state.answer_history     = []       # {question, answer, score, …}
        st.session_state.messages           = []
        st.session_state.report             = None
        st.session_state.last_played_q_id   = None
        st.session_state.interview_start_time = None
        # ── media controls ──
        st.session_state.mic_muted          = False
        st.session_state.cam_off            = False
        # ── user profile ──
        st.session_state.user_profile       = {}

init_session_state()

# ---------------------------------------------------------------------------
# HELPER — elapsed timer string
# ---------------------------------------------------------------------------
def get_elapsed_time() -> str:
    """Return HH:MM elapsed since interview started."""
    if not st.session_state.interview_start_time:
        return "00:00"
    delta = datetime.now() - st.session_state.interview_start_time
    mins  = int(delta.total_seconds() // 60)
    secs  = int(delta.total_seconds() % 60)
    return f"{mins:02d}:{secs:02d}"

# ---------------------------------------------------------------------------
# HELPER — reset interview for a fresh session
# ---------------------------------------------------------------------------
def reset_interview():
    """Clear all interview-related state for a new session."""
    st.session_state.interview_active    = False
    st.session_state.interview_complete  = False
    st.session_state.interview_stage     = 'idle'
    st.session_state.intro_spoken        = False
    st.session_state.current_question    = None
    st.session_state.question_history    = []
    st.session_state.answer_history      = []
    st.session_state.messages            = []
    st.session_state.report              = None
    st.session_state.last_played_q_id    = None
    st.session_state.interview_start_time = None
    st.session_state.mic_muted           = False
    st.session_state.cam_off             = False
    # Reset selector history so questions restart cleanly
    st.session_state.selector.reset_history()

# ---------------------------------------------------------------------------
# HELPER — process a submitted answer (voice or text)
# ---------------------------------------------------------------------------
def process_answer(answer_text: str):
    """
    Evaluate the given answer text, store the record, advance to the next
    question or trigger wrap-up.  All feedback is STORED but NOT shown yet
    (deferred until the Report stage).
    """
    q = st.session_state.current_question
    if not q or not answer_text.strip():
        return

    feedback = st.session_state.evaluator.evaluate_answer(q['id'], answer_text)

    record = {
        "question_id" : q['id'],
        "question"    : q['question'],
        "answer"      : answer_text,
        "score"       : feedback["score"],
        "topic"       : q.get("topic", "general"),
        "difficulty"  : get_difficulty_level(q),
        "feedback"    : feedback,
        "timestamp"   : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.answer_history.append(record)
    st.session_state.question_history.append(q['id'])

    st.session_state.selector.update_performance(
        q['id'], feedback["score"], q.get("topic", "general")
    )

    total_q = 10   # configurable interview length
    if len(st.session_state.answer_history) < total_q:
        if st.session_state.get("csp_toggle") and st.session_state.get("planned_questions"):
            next_q = st.session_state.planned_questions.pop(0)
            st.session_state.current_question = next_q
            st.session_state.last_played_q_id = None
        else:
            next_q = st.session_state.selector.select_next_question(
                st.session_state.user_profile, st.session_state.answer_history
            )
            st.session_state.current_question = next_q
            st.session_state.last_played_q_id = None   # triggers TTS for new question
    else:
        # All questions done → wrapup stage
        st.session_state.interview_stage = 'wrapup'
        st.session_state.current_question = None

# ===========================================================================
# ██████████████████████  SIDEBAR  ██████████████████████
# ===========================================================================
with st.sidebar:
    # ── Branding ──
    st.markdown("""
        <div style="text-align:center; padding:18px 10px;">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        width:90px; height:90px; border-radius:50%; margin:0 auto 12px;
                        display:flex; align-items:center; justify-content:center;
                        box-shadow:0 8px 20px rgba(102,126,234,0.35);">
                <span style="font-size:2.6rem; color:white;">🎯</span>
            </div>
            <h2 style="color:#1E293B; margin:0; font-size:1.6rem;">AI Interview Coach</h2>
            <p style="color:#64748B; margin:4px 0 0; font-size:0.85rem;">Professional Edition v3.0</p>
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);
                        height:3px; width:50px; margin:12px auto 0; border-radius:3px;"></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Profile form ──
    # ── Profile form ──

    with st.expander("👤 Your Profile", expanded=not st.session_state.user_profile.get("profile_complete", False)):
        with st.form("profile_form", clear_on_submit=False):
            st.markdown("##### 📋 Personal Information")
            col_a, col_b = st.columns(2)
            with col_a:
                name = st.text_input("Full Name *", value=st.session_state.user_profile.get("name",""),
                                     placeholder="Jane Doe")
            with col_b:
                email = st.text_input("Email *", value=st.session_state.user_profile.get("email",""),
                                      placeholder="jane@example.com")

            st.markdown("---")
            st.markdown("##### 🎯 Career Goals")

            target_role = st.selectbox("Target Role *", [
                "Software Engineer", "Data Scientist", "Backend Developer",
                "Frontend Developer", "DevOps Engineer", "Data Analyst",
                "Machine Learning Engineer", "Full Stack Developer",
                "Cloud Architect", "Product Manager", "QA Engineer"
            ])

            experience = st.radio("Experience Level *", [
                "Entry Level (0-2 years)", "Mid Level (3-5 years)",
                "Senior Level (5+ years)", "Lead/Manager (8+ years)"
            ], index=0, horizontal=False)

            st.markdown("##### 💻 Skills")
            col_c, col_d = st.columns(2)
            with col_c:
                langs = st.multiselect("Languages", ["Python","Java","JavaScript","C++","C#","Go","Rust","PHP"],
                                       default=[s for s in st.session_state.user_profile.get("skills",[]) if s in ["Python","Java","JavaScript","C++","C#","Go","Rust","PHP"]])
                dbs   = st.multiselect("Databases",  ["SQL","MongoDB","PostgreSQL","MySQL","Redis"],
                                       default=[s for s in st.session_state.user_profile.get("skills",[]) if s in ["SQL","MongoDB","PostgreSQL","MySQL","Redis"]])
            with col_d:
                fws   = st.multiselect("Frameworks", ["React","Django","Flask","Spring","Angular","TensorFlow"],
                                       default=[s for s in st.session_state.user_profile.get("skills",[]) if s in ["React","Django","Flask","Spring","Angular","TensorFlow"]])
                tools = st.multiselect("Tools",      ["AWS","Docker","Kubernetes","Git","Linux","Jenkins"],
                                       default=[s for s in st.session_state.user_profile.get("skills",[]) if s in ["AWS","Docker","Kubernetes","Git","Linux","Jenkins"]])

            all_skills = langs + dbs + fws + tools

            _, col_mid, _ = st.columns([1,2,1])
            with col_mid:
                submitted = st.form_submit_button("🚀 SAVE PROFILE", use_container_width=True, type="primary")

            if submitted:
                errors = []
                if not name:  errors.append("Name is required")
                if not email or "@" not in email: errors.append("Valid email required")
                if len(all_skills) < 1: errors.append("Select at least 1 skill")
                if errors:
                    for e in errors: st.error(f"❌ {e}")
                else:
                    st.session_state.user_profile = {
                        "name": name, "email": email,
                        "target_role": target_role,
                        "experience_level": experience.split("(")[0].strip().lower(),
                        "skills": all_skills, "profile_complete": True,
                        "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.success("✅ Profile saved! Click Start Interview below.")
                    st.balloons()

    # ── Voice Selector ──
    with st.expander("🎙️ Voice Settings", expanded=False):
        voice_options = {
            "Professional Female (Jenny)": "en-US-JennyNeural",
            "Professional Male (Guy)": "en-US-GuyNeural",
            "Indian English Female (Neerja)": "en-IN-NeerjaNeural"
        }
        selected_label = st.selectbox(
            "Choose AI voice:",
            options=list(voice_options.keys()),
            index=0
        )
        st.session_state.selected_voice = voice_options[selected_label]
        
        if st.button("🔊 Test Voice", use_container_width=True):
            text_to_speech_autoplay(f"Hello! This is a test of the {selected_label} voice.")

    # ── Interview Controls ──
    with st.expander("⚙️ Interview Settings", expanded=False):
        if not st.session_state.interview_active and not st.session_state.interview_complete:
            st.checkbox("⚙️ Use Pre-Planned Syllabus (CSP & Backtracking)", value=False, key="csp_toggle")
            st.checkbox("⚡ Enable AI-Enhanced Mode (Gemini)", value=False, key="ai_enhanced_mode")
            
            if st.button("🚀 START NEW INTERVIEW", use_container_width=True):
                if st.session_state.user_profile:
                    reset_interview()
                    
                    if st.session_state.get("csp_toggle"):
                        planner = ConstraintSatisfactionPlanner(st.session_state.kb)
                        planned = planner.generate_interview_plan()
                        if not planned:
                            st.warning("CSP planner could not find a valid plan. Switching to Best-First Search.")
                            import time; time.sleep(2.5)
                            first_q = st.session_state.selector.select_next_question(st.session_state.user_profile, [])
                            st.session_state.planned_questions = []
                        else:
                            st.session_state.planned_questions = planned
                            first_q = st.session_state.planned_questions.pop(0)
                    else:
                        first_q = st.session_state.selector.select_next_question(
                            st.session_state.user_profile, []
                        )
                        
                    st.session_state.current_question    = first_q
                    st.session_state.interview_active    = True
                    st.session_state.interview_stage     = 'intro'
                    st.session_state.interview_start_time = datetime.now()
                    st.rerun()
                else:
                    st.warning("⚠️ Please complete and save your profile first!")

        if st.session_state.interview_active:
            if st.button("⏹️ END INTERVIEW EARLY", use_container_width=True):
                with st.spinner("Generating report…"):
                    st.session_state.report = st.session_state.reporter.generate_report(
                        st.session_state.user_profile, st.session_state.answer_history
                    )
                st.session_state.interview_active   = False
                st.session_state.interview_complete = True
                st.session_state.interview_stage    = 'report'
                st.rerun()

        if st.session_state.interview_complete:
            if st.button("🔄 START NEW SESSION", use_container_width=True):
                reset_interview()
                st.rerun()
                
    # ── Knowledge Explorer (BFS) ──
    with st.expander("📚 Study Topics (BFS)", expanded=False):
        st.markdown("**Unit II: Uninformed Search (BFS)**\\nTraversing Root → Topic → Difficulty → Question")
        bfs_nodes = st.session_state.kb.explore_topics_bfs()
        for node in bfs_nodes:
            if node["level"] == "topic":
                st.markdown(f"**📘 {node['name']}**")
            elif node["level"] == "difficulty":
                st.markdown(f"&nbsp;&nbsp;↳ *{node['name']}*")
            elif node["level"] == "question":
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• [Q{node['id']}] {node['name']}")

    st.markdown("---")

    # ── Live stats ──
    if st.session_state.interview_active:
        st.markdown('<div class="sidebar-header">📊 Live Stats</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        answered = len(st.session_state.answer_history)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:1.4rem; color:#667eea;">📝</div>
                    <div class="metric-value">{answered}</div>
                    <div class="metric-label">Answered</div>
                </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:1.4rem; color:#667eea;">⏱️</div>
                    <div class="metric-value" style="font-size:1.3rem;">{get_elapsed_time()}</div>
                    <div class="metric-label">Elapsed</div>
                </div>""", unsafe_allow_html=True)

        prog = min(answered / 10, 1.0)
        st.progress(prog)
        st.caption(f"Progress: {answered}/10 questions")
        st.markdown("---")

    # ── Tips ──
    with st.expander("💡 Interview Tips"):
        st.markdown("""
- Speak clearly and at a moderate pace
- Use the **text box** as a fallback if mic fails
- Be specific — give examples from experience
- Answer in full sentences for better scoring
- Click **Record Answer** then speak; click again to stop
        """)

# ===========================================================================
# ██████████████████████  MAIN CONTENT  ██████████████████████
# ===========================================================================

# ── Page title ──
_, hcol, _ = st.columns([1, 3, 1])
with hcol:
    st.markdown('<h1 style="font-size:2.8rem;font-weight:700;'
                'background:linear-gradient(135deg,#667eea,#764ba2);'
                '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
                'text-align:center;margin-bottom:0.3rem;">🎯 AI Interview Coach</h1>',
                unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#718096;font-size:1.05rem;margin-bottom:0;">'
                'Professional Interview Preparation with Real-time AI Feedback</p>',
                unsafe_allow_html=True)

st.markdown("---")

# ===========================================================================
# ██  STAGE 0: WELCOME (idle)  ██
# ===========================================================================
if not st.session_state.interview_active and not st.session_state.interview_complete:

    st.markdown("""
        <div class="hero-box">
            <h2 style="font-size:2.2rem;margin-bottom:0.6rem;">
                Welcome to Your AI Interview Room 🎙️
            </h2>
            <p style="font-size:1.1rem;opacity:0.9;">
                Practice real interview conversations with live camera, voice answers, and instant AI analysis.
            </p>
        </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in [
        (c1, "📹", "Live Camera Room", "Webcam-enabled interview room mimicking real video calls"),
        (c2, "🎙️", "Voice Answers",   "Speak your answers — automatic speech recognition"),
        (c3, "📊", "Post-Interview Report", "Full evaluation only after completing all questions"),
    ]:
        with col:
            st.markdown(f"""
                <div style="background:white;padding:1.5rem;border-radius:14px;
                            text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.06);">
                    <div style="font-size:2.5rem;margin-bottom:0.7rem;">{icon}</div>
                    <h4 style="margin:0 0 0.5rem;">{title}</h4>
                    <p style="color:#666;font-size:0.9rem;margin:0;">{desc}</p>
                </div>""", unsafe_allow_html=True)

    st.markdown("")

    with st.expander("📋 How the Interview Works", expanded=True):
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""
**Step-by-step flow:**
1. Save your profile in the sidebar
2. Click **Start New Interview**
3. AI greets you and begins asking questions
4. Speak into your microphone (or type) to answer
5. After all 10 questions, the AI wraps up
6. View your full performance report
            """)
        with col_r:
            st.markdown("""
**Tips for best results:**
✅ Use Chrome or Edge for best camera/mic support
✅ Allow camera & microphone when prompted
✅ Speak clearly — pause before and after your answer
✅ Use the text box as a fallback if voice fails
✅ Complete all 10 questions for a full report
            """)

    if st.session_state.user_profile:
        _, sc, _ = st.columns([1, 2, 1])
        with sc:
            if st.button("🚀 START YOUR INTERVIEW", use_container_width=True):
                reset_interview()
                
                if st.session_state.get("csp_toggle"):
                    planner = ConstraintSatisfactionPlanner(st.session_state.kb)
                    planned = planner.generate_interview_plan()
                    if not planned:
                        st.warning("CSP planner could not find a valid plan. Switching to Best-First Search.")
                        import time; time.sleep(2.5)
                        first_q = st.session_state.selector.select_next_question(st.session_state.user_profile, [])
                        st.session_state.planned_questions = []
                    else:
                        st.session_state.planned_questions = planned
                        first_q = st.session_state.planned_questions.pop(0)
                else:
                    first_q = st.session_state.selector.select_next_question(
                        st.session_state.user_profile, []
                    )
                    
                st.session_state.current_question    = first_q
                st.session_state.interview_active    = True
                st.session_state.interview_stage     = 'intro'
                st.session_state.interview_start_time = datetime.now()
                st.rerun()
    else:
        st.info("👈 **Complete your profile in the sidebar to unlock the Start button.**")

# ===========================================================================
# ██  STAGE 1-3: ACTIVE INTERVIEW  ██
# ===========================================================================
if st.session_state.interview_active:

    profile = st.session_state.user_profile
    cand_name = profile.get("name", "Candidate")
    q     = st.session_state.current_question
    stage = st.session_state.interview_stage
    answered = len(st.session_state.answer_history)

    # ── Meeting header bar ──
    mic_icon = "🔇" if st.session_state.mic_muted else "🎤"
    cam_icon = "📷" if st.session_state.cam_off   else "📹"
    st.markdown(f"""
        <div class="meet-header">
            <div>
                <span class="meet-title">
                    <span class="status-dot dot-live"></span>
                    AI Interview Session &mdash; {profile.get('target_role','')}
                </span><br>
                <span class="meet-meta">Candidate: {cand_name} &nbsp;|&nbsp;
                    Q{answered + 1}/10 &nbsp;|&nbsp; &#9201; {get_elapsed_time()}
                </span>
            </div>
            <div style="display:flex;gap:18px;font-size:1.3rem;">
                <span>{mic_icon}</span>
                <span>{cam_icon}</span>
                <span style="color:#ea4335;">&#9210;</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── FIX 3: Cache TTS so it plays only ONCE per greeting (not on every rerun) ──
    if stage == 'intro':
        if not st.session_state.intro_spoken:
            if 'intro_message' not in st.session_state:
                st.session_state.intro_message = None
                
                # Feature 1: Personalised Voice Introduction (Gemini)
                if st.session_state.get('ai_enhanced_mode', False):
                    import streamlit as st
                    from utils import call_gemini
                    prompt = (
                        f"You are an AI interview coach. Write a short 2-sentence welcome message "
                        f"for {cand_name} who is interviewing for a {profile.get('target_role', 'Software Engineer')} "
                        f"position at {profile.get('experience_level', 'entry')} level. "
                        f"Be warm, professional, and encouraging. No more than 40 words."
                    )
                    llm_greeting = call_gemini(prompt, feature_name="Feature 1: Voice Intro")
                    if llm_greeting:
                        st.session_state.intro_message = llm_greeting

            greeting = st.session_state.intro_message or (
                f"Hi {cand_name}, I'm an AI, your interviewer today. "
                f"Really glad you could make it. We'll be going through some {profile.get('target_role', 'Software Engineer')} questions today — should take about 15-20 minutes. "
                "Feel free to take your time with each answer, there's no rush. "
                "Ready to get started?"
            )
            
            # 1.2 Human-like Opening Sequence
            text_to_speech_autoplay("Hello? Can you hear me okay? Great, give me just one second...")
            time.sleep(1.5)
            text_to_speech_autoplay(greeting)
            st.session_state.intro_spoken = True

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("👉 I'm Ready — Ask First Question", use_container_width=True, type="primary", key="btn_ready"):
                text_to_speech_autoplay("Perfect, let's dive in. First question:")
                time.sleep(0.8)
                st.session_state.interview_stage = 'questions'
                st.rerun()

    # ── Camera panel: pure browser-side getUserMedia() — no server relay needed ──
    # This is exactly how Google Meet shows your self-view: the browser accesses
    # the camera locally and pipes it into a <video> element. No WebRTC STUN/TURN
    # server is involved for self-preview.

    cam_hidden = "true" if st.session_state.get('cam_off', False) else "false"

    camera_html = f"""
    <div style="
        background:#1a1b1e;
        border:2px solid #3c4043;
        border-radius:14px;
        overflow:hidden;
        font-family:'Inter',sans-serif;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
    ">
        <!-- Header bar -->
        <div style="
            padding:10px 18px;
            display:flex;
            justify-content:space-between;
            align-items:center;
            border-bottom:1px solid #2d2f31;
        ">
            <span style="color:#9aa0a6;font-size:0.85rem;font-weight:500;">
                &#128249;&nbsp; Live Camera &mdash;
                <strong style="color:#e8eaed;">{cand_name}</strong>
            </span>
            <span id="liveTag" style="
                background:rgba(234,67,53,0.18);color:#ea4335;
                font-size:0.7rem;padding:3px 10px;border-radius:20px;
                font-weight:600;letter-spacing:0.4px;
            ">&#9210; LIVE</span>
        </div>

        <!-- Video element -->
        <div id="videoWrapper" style="position:relative;background:#000;text-align:center;">
            <video id="localVideo"
                autoplay playsinline muted
                style="
                    width:100%;
                    height:490px;
                    object-fit:cover; /* Fill the card nicely */
                    display:block;
                    transform:scaleX(-1);  /* Mirror like every selfie camera */
                "
            ></video>

            <!-- Overlay shown when camera is off -->
            <div id="camOff" style="
                display:none;
                position:absolute;top:0;left:0;right:0;bottom:0;
                background:#0f172a;
                align-items:center;justify-content:center;
                flex-direction:column;
                color:#475569;
                min-height:300px;
            ">
                <div style="font-size:2.8rem;">&#128247;</div>
                <p style="margin:10px 0 0;font-size:0.9rem;">Camera is off</p>
                <p style="font-size:0.75rem;opacity:0.55;margin-top:4px;">
                    Click <strong style="color:#9aa0a6;">Cam On</strong> below
                </p>
            </div>

            <!-- Permission error overlay -->
            <div id="camError" style="
                display:none;
                position:absolute;top:0;left:0;right:0;bottom:0;
                background:#1a1b1e;
                align-items:center;justify-content:center;
                flex-direction:column;
                color:#64748b;
                min-height:300px;
            ">
                <div style="font-size:2.8rem;">&#128247;</div>
                <p style="margin:10px 0 0;font-size:0.9rem;color:#f87171;">
                    Camera permission denied
                </p>
                <p style="font-size:0.75rem;opacity:0.7;margin-top:6px;text-align:center;max-width:280px;">
                    Click the camera icon in your browser address bar and allow camera access,
                    then refresh the page.
                </p>
            </div>
        </div>
    </div>

    <script>
    (function() {{
        var video      = document.getElementById('localVideo');
        var camOffDiv  = document.getElementById('camOff');
        var camErrDiv  = document.getElementById('camError');
        var liveTag    = document.getElementById('liveTag');
        var currentStream = null;
        var isCamOff = {cam_hidden};   // Python injects 'true' or 'false'

        function startCamera() {{
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
                camErrDiv.style.display = 'flex';
                return;
            }}
            navigator.mediaDevices.getUserMedia({{ video: true, audio: false }})
                .then(function(stream) {{
                    currentStream = stream;
                    video.srcObject = stream;
                    video.style.display = 'block';
                    camOffDiv.style.display  = 'none';
                    camErrDiv.style.display  = 'none';
                    liveTag.style.display    = 'inline';
                }})
                .catch(function(err) {{
                    console.warn('Camera error:', err);
                    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {{
                        camErrDiv.style.display = 'flex';
                    }} else if (err.name === 'NotFoundError') {{
                        camErrDiv.innerHTML = '<div style="font-size:2.5rem;">&#128247;</div><p style="margin:10px 0 0;color:#f87171;">No camera detected</p>';
                        camErrDiv.style.display = 'flex';
                    }} else {{
                        camErrDiv.style.display = 'flex';
                    }}
                }});
        }}

        function stopCamera() {{
            if (currentStream) {{
                currentStream.getTracks().forEach(function(t) {{ t.stop(); }});
                currentStream = null;
            }}
            video.srcObject = null;
            video.style.display    = 'none';
            camOffDiv.style.display = 'flex';
            liveTag.style.display  = 'none';
        }}

        // Kick off based on current Streamlit cam_off state
        if (isCamOff) {{
            stopCamera();
        }} else {{
            startCamera();
        }}
    }})();
    </script>
    """

    col_avatar, col_cam = st.columns(2)
    with col_avatar:
        avatar_emotion = "listening" if not st.session_state.mic_muted else "neutral"
        status_color = "#10b981" if not st.session_state.mic_muted else "#9aa0a6"
        status_bg = "rgba(16,185,129,0.1)" if not st.session_state.mic_muted else "rgba(154,160,166,0.1)"
        status_text = "Listening" if not st.session_state.mic_muted else "Waiting"
        
        v_label = "Interviewer"
        for label, val in voice_options.items():
            if val == st.session_state.get('selected_voice'):
                v_label = label
                break
                
        avatar_html = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        @keyframes pulse {{
            0% {{ opacity:1; transform:scale(1); }}
            50% {{ opacity:0.6; transform:scale(1.3); }}
            100% {{ opacity:1; transform:scale(1); }}
        }}
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-10px); }}
            60% {{ transform: translateY(-5px); }}
        }}
        @keyframes float {{
            0% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-6px); }}
            100% {{ transform: translateY(0); }}
        }}
        .pulse {{ animation: pulse 2s infinite; }}
        .bounce {{ animation: bounce 2s infinite; }}
        .float {{ animation: float 3s ease-in-out infinite; }}
        </style>
        <div style="
            background:#1a1b1e;
            border:2px solid #3c4043;
            border-radius:14px;
            padding: 20px;
            height: 496px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: 'Inter', sans-serif;
            box-sizing: border-box;
            box-shadow: 0 0 15px {"rgba(16,185,129,0.15)" if not st.session_state.mic_muted else "rgba(154,160,166,0.15)"};
        ">
            <div style="margin-bottom:auto; color:#9aa0a6; font-size:0.85rem; font-weight:500; width:100%; text-align:left; border-bottom:1px solid #2d2f31; padding-bottom:10px;">
                🤖 AI Coach — <strong style="color:#e8eaed;">{v_label}</strong>
            </div>
            
            <div style="margin: auto 0; display:flex; flex-direction:column; align-items:center;">
                {get_robot_avatar(avatar_emotion)}
                <div style="margin-top:35px; padding:8px 20px; border-radius:20px; font-size:0.8rem; font-weight:600; 
                            background:{status_bg}; color:{status_color}; text-transform:uppercase; letter-spacing:0.5px;">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:currentColor; margin-right:6px; animation: pulse 1.5s infinite;"></span>
                    {status_text}
                </div>
            </div>
        </div>
        """
        components.html(avatar_html, height=540, scrolling=False)
        
    with col_cam:
        components.html(camera_html, height=540, scrolling=False)

    # ── Meeting control bar ──
    st.markdown("")
    ctrl1, ctrl2, ctrl3, _ = st.columns([1, 1, 1, 3])
    with ctrl1:
        mic_lbl = "&#128263; Unmute" if st.session_state.mic_muted else "&#127908; Mute"
        if st.button("🔇 Unmute" if st.session_state.mic_muted else "🎙️ Mute", key="mute_btn"):
            st.session_state.mic_muted = not st.session_state.mic_muted
            st.rerun()
    with ctrl2:
        if st.button("📷 Cam On" if st.session_state.cam_off else "📷 Cam Off", key="cam_btn"):
            st.session_state.cam_off = not st.session_state.cam_off
            st.rerun()
    with ctrl3:
        if st.button("🔴 End Interview", key="end_btn"):
            with st.spinner("Generating your performance report…"):
                st.session_state.report = st.session_state.reporter.generate_report(
                    profile, st.session_state.answer_history
                )
            st.session_state.interview_active   = False
            st.session_state.interview_complete = True
            st.session_state.interview_stage    = 'report'
            st.rerun()

    st.markdown("---")

    # ── WRAPUP STAGE ──
    if stage == 'wrapup':
        if "wrapup_started" not in st.session_state:
            st.session_state.wrapup_started = True
            
            # 1.3 Human-like Closing Sequence
            closing1 = f"That was the last question, {cand_name}. Really appreciate your time today."
            text_to_speech_autoplay(closing1)
            time.sleep(TIMING["closing_between_lines"])
            
            # Determine strongest topic
            strongest_topic = "general concepts"
            if st.session_state.answer_history:
                # Group by topic and average
                topic_scores = {}
                for rec in st.session_state.answer_history:
                    t = rec.get("topic", "general")
                    if t not in topic_scores: topic_scores[t] = []
                    topic_scores[t].append(rec["score"])
                if topic_scores:
                    avgs = {t: sum(s)/len(s) for t, s in topic_scores.items()}
                    strongest_topic = max(avgs, key=avgs.get)
            
            closing2 = f"You had some strong moments, especially on {strongest_topic}. I'll put together your feedback report now."
            
            if st.session_state.get('ai_enhanced_mode', False):
                try:
                    from utils import call_gemini
                    prompt = (
                        f"You are an AI interview coach concluding an interview with {cand_name}. "
                        f"The candidate's strongest topic was {strongest_topic}. "
                        f"Write a warm 2-sentence closing statement celebrating their strong moments on that topic "
                        f"and letting them know you'll put together their feedback report now. Be extremely conversational."
                    )
                    llm_close = call_gemini(prompt, feature_name="Feature: Voice Closing")
                    if llm_close:
                        closing2 = llm_close
                except Exception:
                    pass
            
            text_to_speech_autoplay(closing2)
            time.sleep(1.5)
        st.markdown("""
            <div style="background:linear-gradient(135deg,#065f46,#047857);
                        color:white;padding:2rem;border-radius:14px;text-align:center;margin:1rem 0;">
                <h3 style="margin:0 0 0.5rem;">🎉 All Questions Completed!</h3>
                <p style="margin:0;opacity:0.9;">Generating your comprehensive performance report…</p>
            </div>""", unsafe_allow_html=True)

        with st.spinner("🤖 Analysing all your answers…"):
            time.sleep(2)   # dramatic pause for TTS to finish
            st.session_state.report = st.session_state.reporter.generate_report(
                profile, st.session_state.answer_history
            )
        st.session_state.interview_active   = False
        st.session_state.interview_complete = True
        st.session_state.interview_stage    = 'report'
        st.rerun()

    # ── QUESTIONS STAGE ──
    elif stage == 'questions' and q:

        # FIX 3 (questions): Cache TTS audio per question ID in session_state.
        # This ensures the AI voice plays exactly once per new question and is
        # NEVER re-requested from Google's TTS server on subsequent reruns
        # (which was causing the audio to restart / break mid-sentence).
        if st.session_state.last_played_q_id != q['id']:
            if answered > 0:
                # 1.4 Acknowledgement and Transitions
                ack = random.choice(ACKNOWLEDGEMENTS)
                trans = random.choice(TRANSITIONS)
                text_to_speech_autoplay(ack)
                time.sleep(TIMING["after_acknowledgement"])
                text_to_speech_autoplay(trans)
                time.sleep(TIMING["before_question"])
                text_to_speech_autoplay(q['question'])
                time.sleep(TIMING["after_question_spoken"])
            else:
                text_to_speech_autoplay(q['question'])
                time.sleep(TIMING["after_question_spoken"])
                
            st.session_state.last_played_q_id = q['id']

        # ── Part 3.3 Score Display After Each Answer ──
        if st.session_state.answer_history:
            last_record = st.session_state.answer_history[-1]
            last_q = last_record['question']
            sc = last_record['score']
            last_q_id = last_record['question_id']
            last_q_data = st.session_state.kb.get_question_by_id(last_q_id)
            
            sc_icon = "✅" if sc >= 7 else "⚠️" if sc >= 5 else "❌"
            sc_color = "#10b981" if sc >= 7 else "#f59e0b" if sc >= 5 else "#ef4444"
            sc_text = "Good Answer" if sc >= 7 else "Needs Details" if sc >= 5 else "Needs Practice"
            
            fb = last_record['feedback']
            missing_c = len(fb.get('missing_concepts', []))
            total_concepts = len(last_q_data.get('concepts', [])) if last_q_data else 0
            matched_concepts = max(0, total_concepts - missing_c)
            
            ans_lower = last_record['answer'].lower()
            total_kw = len(last_q_data.get('keywords', [])) if last_q_data else 0
            matched_kw_count = sum(1 for k in last_q_data.get('keywords', []) if k.lower() in ans_lower) if last_q_data else 0
            
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155; border-radius:12px; padding:1.2rem; margin-bottom:1rem; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.8rem;">
                    <span style="color:#e2e8f0; font-size:1.1rem; font-weight:600;">Your Score: {sc:.1f} / 10 {sc_icon}</span>
                    <span style="color:{sc_color}; font-weight:600;">{sc_text}</span>
                </div>
            """, unsafe_allow_html=True)
            st.progress(sc / 10.0)
            
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; margin-top: 0.8rem; font-size:0.9rem; color:#94a3b8;">
                    <span>Keywords matched: {matched_kw_count}/{total_kw}</span>
                    <span>Concepts covered: {matched_concepts}/{total_concepts}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Part 2 — Instant Suggestion Button
            instant_key = f"instant_tip_{last_q_id}"
            if instant_key not in st.session_state:
                if st.button("💡 Get Instant Coaching Tip", key=f"btn_tip_{last_q_id}"):
                    with st.spinner("Getting your tip..."):
                        if st.session_state.get('ai_enhanced_mode', False):
                            try:
                                from utils import call_gemini
                                matched_kw_list = [k for k in last_q_data.get('keywords', []) if k.lower() in ans_lower] if last_q_data else []
                                missing_c_list = fb.get('missing_concepts', [])
                                prompt = (
                                    f"You are a friendly interview coach giving quick real-time advice.\n"
                                    f"The candidate just answered this interview question: '{last_q}'\n"
                                    f"Their answer was: '{last_record['answer']}'\n"
                                    f"They scored {sc}/10.\n"
                                    f"They correctly mentioned: {matched_kw_list}\n"
                                    f"They missed these concepts: {missing_c_list}\n\n"
                                    f"Give ONE specific, actionable tip they can use RIGHT NOW to improve "
                                    f"this answer if asked again. Start with what they did right in one "
                                    f"sentence, then give the improvement tip. Maximum 3 sentences total. "
                                    f"Be conversational and encouraging, like a friend helping you prep. "
                                    f"No bullet points, no headers."
                                )
                                tip = call_gemini(prompt, feature_name="Feature: Instant Tip")
                                if tip:
                                    st.session_state[instant_key] = tip
                                else:
                                    st.session_state[instant_key] = "Tip unavailable right now — check the AI Coach Feedback below for suggestions"
                            except Exception:
                                st.session_state[instant_key] = "Tip unavailable right now — check the AI Coach Feedback below for suggestions"
                        else:
                            st.session_state[instant_key] = "Tip unavailable right now — check the AI Coach Feedback below for suggestions"
                    st.rerun()
            
            if instant_key in st.session_state:
                st.markdown(f"""
                <div style="background:#fffbeb; border-left:4px solid #f59e0b; padding:1rem; border-radius:8px; margin-bottom:1.5rem;">
                    <div style="color:#b45309; font-weight:700; margin-bottom:0.4rem; font-size:0.9rem;">💡 Quick Coaching Tip</div>
                    <div style="color:#92400e; font-size:0.95rem;">{st.session_state[instant_key]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        predicted_candidates = []
        if not (st.session_state.get("csp_toggle") and st.session_state.get("planned_questions")):
            predicted_candidates = st.session_state.selector.get_predicted_questions(
                st.session_state.user_profile, st.session_state.answer_history, n=3
            )

        with st.expander("🧠 Internal AI Logic (Top Candidate Questions)"):
            if st.session_state.get("csp_toggle"):
                st.write("Using Constraint Satisfaction (Pre-planned Syllabus):")
                if st.session_state.planned_questions:
                    for i, planned_q in enumerate(st.session_state.planned_questions[:3]):
                        st.write(f"{i+1}. {planned_q['question']}")
                else:
                    st.write("No more questions planned.")
            else:
                st.write("Using Best-First Search heuristics:")
                if predicted_candidates:
                    for i, (score, cand_q) in enumerate(predicted_candidates):
                        extra = ""
                        if score > 0.8:
                            extra = " *(high priority due to weakness focus)*"
                        st.write(f"{i+1}. **\"{cand_q['question']}\"** — Score: `{score:.2f}` {extra}")
                else:
                    st.write("No more candidate questions available.")

        # ── Question card ──
        diff_level  = get_difficulty_level(q)
        st.markdown(f"""
            <div style="text-align:center; font-size:1.1rem; color:#94a3b8; font-weight:600; text-transform:uppercase; margin-bottom: 0.6rem; margin-top: 1rem;">
                Question {answered + 1} of 10
            </div>
        """, unsafe_allow_html=True)
            
        st.markdown(f"""
            <div style="background:white; color:#1e293b; padding:1.8rem; border-radius:14px; text-align:center; box-shadow:0 10px 25px -5px rgba(0,0,0,0.1); border:1px solid #e2e8f0; margin-bottom:1rem;">
                <div style="font-size:20px; font-weight:600; line-height:1.6; margin-bottom:1rem;">{q['question']}</div>
                <div style="display:inline-block; margin-top:0.4rem;">
                    <span class="badge badge-{diff_level}">{diff_level.title()}</span>
                    <span style="font-size:0.8rem; color:#64748b; margin-left:10px;">📌 Topic: {q.get('topic','General').title()}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Progress dots ──
        dots_html = []
        for i in range(10):
            if i < len(st.session_state.answer_history):
                # Answered: color based on score
                s = st.session_state.answer_history[i]['score']
                dot_color = "#10b981" if s >= 7 else "#f59e0b" if s >= 5 else "#ef4444"
                dots_html.append(f'<div style="width:12px; height:12px; border-radius:50%; background:{dot_color};" title="Score: {s}"></div>')
            elif i == answered:
                # Current
                dots_html.append('<div style="width:12px; height:12px; border-radius:50%; background:#3b82f6; box-shadow:0 0 8px rgba(59,130,246,0.6); animation: pulse 1.5s infinite;"></div>')
            else:
                # Unanswered
                dots_html.append('<div style="width:12px; height:12px; border-radius:50%; background:#e2e8f0; border:1px solid #cbd5e1;"></div>')
        
        st.markdown(f"""<div style="display:flex; justify-content:center; gap:6px; margin-bottom:2rem;">{"".join(dots_html)}</div>""", unsafe_allow_html=True)

        # ── Answer section ──
        st.markdown("#### 🎤 Your Answer")

        # Mic-muted warning
        if st.session_state.mic_muted:
            st.warning("🔇 Your microphone is muted. Click **Unmute** in the controls above, then record.")

        # Voice recording
        voice_answer = None
        if not st.session_state.mic_muted:
            if AUDIO_RECORDER_AVAILABLE:
                st.markdown(
                    '<p style="color:#475569;font-size:0.9rem;">'
                    '🔴 Click the button to record · speak your answer · click again to stop</p>',
                    unsafe_allow_html=True
                )
                audio_bytes = audio_recorder(
                    pause_threshold=3.0,
                    sample_rate=16_000,
                    key=f"audio_{answered}"
                )
                if audio_bytes:
                    with st.spinner("🔄 Transcribing your answer…"):
                        voice_answer = speech_to_text(audio_bytes)
                    if voice_answer:
                        st.markdown(f"""
                            <div style="background:#f0fdf4;border:1px solid #86efac;
                                        border-radius:10px;padding:0.9rem;margin:0.5rem 0;">
                                <div style="color:#166534;font-size:0.8rem;font-weight:600;">
                                    ✅ Transcribed answer:
                                </div>
                                <div style="color:#1e293b;margin-top:4px;">{voice_answer}</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ Could not transcribe. Please speak clearly or use the text box below.")
            else:
                st.info("Install `audio-recorder-streamlit` to enable voice answers.")

        # ── Text fallback ──
        st.markdown(
            '<p style="color:#94a3b8;font-size:0.84rem;">Or type your answer manually:</p>',
            unsafe_allow_html=True
        )
        col_txt, col_btn = st.columns([5, 1])
        with col_txt:
            typed_answer = st.text_area(
                "Type your answer:",
                height=130,
                key=f"typed_{answered}",
                placeholder="Type a detailed answer here… include examples where possible.",
                label_visibility="collapsed"
            )
        with col_btn:
            st.write("")
            st.write("")
            submit_typed = st.button("📤 Submit", key=f"submit_{answered}",
                                     use_container_width=True, type="primary")

        # ── Submission logic — voice takes priority, typed is fallback ──
        final_answer = None
        if voice_answer:
            final_answer = voice_answer
        elif submit_typed and typed_answer.strip():
            final_answer = typed_answer.strip()
        elif submit_typed and not typed_answer.strip():
            st.warning("⚠️ Please type an answer or record your voice before submitting.")

        if final_answer:
            with st.spinner("📝 Saving your answer…"):
                process_answer(final_answer)
                time.sleep(0.5)
            st.rerun()

    # ── Answer history accordion (collapsed by default — no spoilers) ──
    if st.session_state.answer_history:
        with st.expander(f"📋 Answers so far ({len(st.session_state.answer_history)} recorded)", expanded=False):
            for i, rec in enumerate(st.session_state.answer_history, 1):
                st.markdown(f"**Q{i}:** {rec['question']}")
                st.markdown(f"*Your answer:* {rec['answer'][:200]}{'…' if len(rec['answer'])>200 else ''}")
                st.markdown("---")

# ===========================================================================
# ██  STAGE 4: PERFORMANCE REPORT  ██
# ===========================================================================
if st.session_state.interview_complete and st.session_state.report:

    report = st.session_state.report

    st.balloons()
    st.markdown(f"""
        <div style="background:linear-gradient(135deg,#065f46 0%,#047857 100%);
                    padding:2rem; border-radius:16px; color:white; text-align:center; margin:1rem 0 2rem;">
            <h2 style="font-size:2rem;margin-bottom:0.4rem;">🎉 Interview Complete!</h2>
            <p style="opacity:0.9;margin:0;">Here is your comprehensive performance analysis, {report['user_profile'].get('name','Candidate')}.</p>
        </div>""", unsafe_allow_html=True)
        
    if "llm_summary" in report:
        st.markdown(f"""
            <div style="background:#f0fdf4; border-left:5px solid #22c55e; padding:1.5rem; border-radius:10px; margin-bottom:1.5rem;">
                <h4 style="color:#166534; margin-top:0; margin-bottom:0.8rem;">✨ AI Coach Summary</h4>
                <p style="color:#15803d; margin:0; font-size:1.1rem; line-height:1.6;">{report['llm_summary']}</p>
            </div>
        """, unsafe_allow_html=True)

    # ── Summary metric cards ──
    mc1, mc2, mc3, mc4 = st.columns(4)
    score = report['summary']['overall_score']
    score_color = "#10b981" if score >= 7 else "#f59e0b" if score >= 5 else "#ef4444"
    perf_level  = report['summary']['performance_level']

    for col, icon, val, label in [
        (mc1, "⭐", f"<span style='color:{score_color}'>{score}/10</span>", f"Overall · {perf_level.title()}"),
        (mc2, "📝", report['summary']['total_questions'],  "Questions Answered"),
        (mc3, "✅", f"{report['summary']['completion_rate']}%", "Completion Rate"),
        (mc4, "💪", len(report['detailed_analysis']['strongest_topics']), "Strength Areas"),
    ]:
        with col:
            col.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:1.5rem;">{icon}</div>
                    <div class="metric-value">{val}</div>
                    <div class="metric-label">{label}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("")

    # ── Tabs ──
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Summary", "📈 Analytics", "📋 Question Review",
        "📚 Learning Path", "🎯 Recommendations"
    ])

    # ── Tab 1: Topic Summary ──
    with tab1:
        st.subheader("📊 Topic-wise Performance")
        topic_data = [
            {"Topic": t.title(), "Score": d['average_score'],
             "Questions": d['questions_attempted'], "Level": d['level'].title()}
            for t, d in report['detailed_analysis']['by_topic'].items()
        ]
        if topic_data:
            df_topics = pd.DataFrame(topic_data)
            fig_bar = px.bar(df_topics, x='Topic', y='Score',
                             color='Score',
                             color_continuous_scale=['#ef4444','#f59e0b','#10b981'],
                             title="Average Score per Topic", text='Score')
            fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                   yaxis_range=[0, 10])
            st.plotly_chart(fig_bar, use_container_width=True)

    # ── Tab 2: Progress & Difficulty ──
    with tab2:
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("📈 Score Progression")
            prog_data = report['detailed_analysis']['progress_over_time']
            if prog_data:
                df_prog = pd.DataFrame(prog_data)
                fig_line = px.line(df_prog, x='question_number', y='score',
                                   title="Score per Question",
                                   labels={'question_number':'Question #','score':'Score'},
                                   markers=True)
                fig_line.update_traces(line_color='#667eea', line_width=3, marker_size=8)
                fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                                        paper_bgcolor='rgba(0,0,0,0)', yaxis_range=[0,10])
                st.plotly_chart(fig_line, use_container_width=True)
        with col_r:
            st.subheader("📊 Difficulty Breakdown")
            diff_data = report['detailed_analysis']['by_difficulty']
            df_diff = pd.DataFrame([
                {"Difficulty": d.title(), "Score": v['average_score'], "Qs": v['questions_attempted']}
                for d, v in diff_data.items()
            ])
            fig_diff = px.bar(df_diff, x='Difficulty', y='Score',
                              color='Score',
                              color_continuous_scale=['#ef4444','#f59e0b','#10b981'],
                              title="Performance by Difficulty", text='Score')
            fig_diff.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig_diff.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                    yaxis_range=[0,10])
            st.plotly_chart(fig_diff, use_container_width=True)

        col_s, col_w = st.columns(2)
        with col_s:
            st.subheader("✅ Strengths")
            for s in report['detailed_analysis']['strongest_topics']:
                st.markdown(f"""
                    <div style="background:#d1fae5;padding:0.9rem;border-radius:10px;margin:0.4rem 0;">
                        <strong>{s['topic'].title()}</strong>: {s['score']}/10
                        <br><small class="badge badge-{s['level']}">{s['level'].title()}</small>
                    </div>""", unsafe_allow_html=True)
        with col_w:
            st.subheader("🔧 Areas to Improve")
            for w in report['detailed_analysis']['weakest_topics']:
                st.markdown(f"""
                    <div style="background:#fee2e2;padding:0.9rem;border-radius:10px;margin:0.4rem 0;">
                        <strong>{w['topic'].title()}</strong>: {w['score']}/10
                        <br><small class="badge badge-{w['level']}">{w['level'].title()}</small>
                    </div>""", unsafe_allow_html=True)

    # ── Tab 3: Per-question review (simplified to avoid broken HTML) ──
    with tab3:
        st.subheader("📋 Detailed Question-by-Question Review")

        if not st.session_state.answer_history:
            st.info("No answers were recorded.")
        else:
            total_qs = len(st.session_state.answer_history)

            # Overall header
            st.markdown(
                f"**Overall Interview Score:** `{score}/10` · "
                f"**Level:** `{perf_level.replace('_', ' ').title()}`"
            )
            st.markdown("---")

            for i, rec in enumerate(st.session_state.answer_history, 1):
                sc = rec.get("score", 0)
                fb = rec.get("feedback", {}) or {}

                with st.container():
                    st.markdown(f"### Question {i} of {total_qs}")
                    st.markdown(f"**Q:** {rec.get('question', '')}")
                    st.markdown(f"**Score:** `{sc}/10`")

                    st.markdown("**Your answer**")
                    raw_ans = (rec.get("answer") or "").strip()
                    if not raw_ans:
                        st.markdown("_No response detected for this question._")
                    else:
                        st.write(raw_ans)

                    if "llm_feedback" in fb:
                        st.markdown("**✨ AI Coach Feedback**")
                        st.write(fb["llm_feedback"])

                    strengths = fb.get("strengths") or []
                    weaknesses = fb.get("weaknesses") or []
                    suggestions = fb.get("suggestions") or []
                    missing = fb.get("missing_concepts") or []

                    if strengths:
                        st.markdown("**✅ Strengths**")
                        for s in strengths:
                            st.markdown(f"- {s}")

                    if weaknesses or missing:
                        st.markdown("**🔧 Areas to Improve**")
                        for w in weaknesses:
                            st.markdown(f"- {w}")
                        if missing:
                            st.markdown(f"- Missed concepts: {', '.join(missing)}")

                    if suggestions:
                        st.markdown("**💡 Suggestions**")
                        for s in suggestions:
                            st.markdown(f"- {s}")

                    ideal = fb.get("ideal_answer") or {}
                    key_points = ideal.get("key_points") or []
                    example = ideal.get("example") or ""

                    if key_points or example:
                        st.markdown("**🎯 Ideal Answer Outline**")
                        if key_points:
                            for p in key_points:
                                st.markdown(f"- {p}")
                        if example:
                            st.markdown("**Example:**")
                            st.code(example)

                    st.markdown("---")

    # ── Tab 4: Learning path ──
    with tab4:
        st.subheader("📚 Personalised Learning Path")
        for phase in report['learning_path']:
            p_color = {"high":"#ef4444","medium":"#f59e0b","low":"#10b981"}.get(phase['priority'],"#667eea")
            st.markdown(f"""
                <div style="background:white;padding:1.25rem;border-radius:14px;margin:0.8rem 0;
                            border-left:5px solid {p_color};box-shadow:0 3px 8px rgba(0,0,0,0.06);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <strong>🔹 {phase['phase'].title()} Phase</strong>
                        <span style="background:{p_color}20;color:{p_color};padding:2px 12px;
                                     border-radius:20px;font-size:0.78rem;">
                            {phase['priority'].title()} Priority
                        </span>
                    </div>
                    <p style="margin:0.6rem 0 0.2rem;"><strong>Focus:</strong> {phase['focus'].title()}</p>
                    <p style="margin:0.2rem 0;"><strong>Goal:</strong> {phase['goal']}</p>
                    <p style="margin:0.2rem 0;color:#718096;font-size:0.87rem;">
                        ⏱ Est. time: {phase['estimated_time']}
                    </p>
                </div>""", unsafe_allow_html=True)

        st.subheader("📖 Recommended Resources")
        for r in report.get('resources', []):
            st.markdown(f"""
                <div style="background:#f8fafc;padding:0.9rem;border-radius:10px;margin:0.4rem 0;">
                    <a href="{r['url']}" target="_blank"
                       style="text-decoration:none;color:#667eea;font-weight:500;">
                        📘 {r['name']}
                    </a>
                    <span style="float:right;color:#94a3b8;font-size:0.82rem;">{r['type'].title()}</span>
                </div>""", unsafe_allow_html=True)

    # ── Tab 5: Recommendations ──
    with tab5:
        st.subheader("💡 Personalised Recommendations")
        for rec_text in report['recommendations']:
            st.info(rec_text)

        st.subheader("⏭️ Immediate Next Steps")
        for step in report['next_steps']:
            st.success(step)

        st.markdown("---")
        st.subheader("📥 Download Report")
        report_json = json.dumps(report, indent=2, default=str)
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=report_json,
            file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

# ===========================================================================
# FOOTER
# ===========================================================================
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>🎯 AI Interview Coach — Professional Edition v3.0</p>
        <p style="font-size:0.78rem;">
            Powered by Best-First Search · Forward-Chaining Evaluation · Streamlit WebRTC<br>
            Built with ❤️ for serious interview preparation
        </p>
    </div>""", unsafe_allow_html=True)

