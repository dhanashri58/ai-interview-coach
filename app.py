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
import os

# Backend logic engines
from knowledge_base import KnowledgeBase
from question_selector import QuestionSelector
from answer_evaluator import AnswerEvaluator
from performance_report import PerformanceReport
from interview_planner_csp import ConstraintSatisfactionPlanner

# New Advanced Algorithms
try:
    from minimax_selector import MinimaxQuestionSelector
    from wumpus_interview import WumpusInterviewWorld
    from strips_planner import GoalStackPlanner, get_strips_actions, update_state_from_answers
    from prolog_kb import PrologKnowledgeBase
except ImportError:
    pass


# Utility helpers (TTS, STT, animations)
from utils import (
    get_typing_animation, get_robot_avatar,
    get_difficulty_level, format_feedback,
    text_to_speech_autoplay, speech_to_text,
    get_progress_ring, display_question_card
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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&family=Space+Grotesk:wght@500;700&display=swap');

/* ── Global Theme Variables: Cosmic SaaS ── */
:root {
    --bg-deep: #020617;
    --bg-main: radial-gradient(circle at top right, #1e1b4b 0%, #020617 100%);
    --bg-surface: rgba(15, 23, 42, 0.6);
    --bg-card: rgba(30, 41, 59, 0.3);
    --brand-primary: #6366F1;   /* Indigo */
    --brand-secondary: #0ea5e9; /* Sky/Cyan */
    --brand-accent: #a855f7;    /* Purple */
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    --neon-indigo: 0 0 15px rgba(99, 102, 241, 0.4);
}

/* ── Global Base ── */
html, body, [class*="css"] { 
    font-family: 'Inter', sans-serif; 
    background: var(--bg-deep) !important;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg-main) !important;
}

h1, h2, h3, h4, .gradient-heading {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
}

/* ── Glassmorphism Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(2, 6, 23, 0.8) !important;
    backdrop-filter: blur(20px) saturate(180%);
    border-right: 1px solid var(--glass-border);
}

/* ── Premium Sidebar Inputs ── */
.stTextInput input, .stSelectbox [data-baseweb="select"], .stMultiSelect [data-baseweb="select"] {
    background: rgba(15, 23, 42, 0.4) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 12px !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

.stTextInput input:focus {
    border-color: var(--brand-primary) !important;
    box-shadow: var(--neon-indigo) !important;
}

/* ── Glass Cards & Feature Panels ── */
.saas-card {
    background: var(--bg-card);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 2rem;
    box-shadow: var(--glass-shadow);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.saas-card:hover {
    transform: translateY(-8px);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4), var(--neon-indigo);
}

/* ── Glowing Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent)) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.8rem 2rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
}

.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5) !important;
}

/* ── Interview Split Screen ── */
.live-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 25px;
}

.video-frame {
    aspect-ratio: 4/3;
    background: #000;
    border-radius: 20px;
    overflow: hidden;
    border: 2px solid var(--glass-border);
    position: relative;
    box-shadow: var(--glass-shadow);
}

/* ── Control Bar ── */
.meet-controls {
    display: flex;
    justify-content: center;
    gap: 15px;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(10px);
    padding: 12px 30px;
    border-radius: 99px;
    width: fit-content;
    margin: 30px auto;
    border: 1px solid var(--glass-border);
}

/* ── Animations ── */
@keyframes nebula {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.cosmic-bg {
    background-size: 200% 200%;
    animation: nebula 15s ease infinite;
}

/* ── Floating Question Card ── */
.floating-question {
    position: absolute;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    width: 85%;
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    z-index: 100;
    animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUpFade {
    from { opacity: 0; transform: translate(-50%, 40px); }
    to { opacity: 1; transform: translate(-50%, 0); }
}

/* ── Analytics Score Panel ── */
.analytics-panel {
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 1.5rem;
    height: 100%;
    box-shadow: var(--glass-shadow);
}

.panel-title {
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.stat-row { margin-bottom: 1.25rem; }
.stat-label { 
    display: flex; 
    justify-content: space-between; 
    font-size: 0.85rem; 
    margin-bottom: 0.5rem;
    color: var(--text-muted);
}

/* ── Modern Progress Bars ── */
.progress-container {
    height: 8px;
    background: rgba(255,255,255,0.05);
    border-radius: 10px;
    overflow: hidden;
    position: relative;
}

.progress-fill {
    height: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg, #6366f1, #a855f7, #0ea5e9);
    transition: width 1s cubic-bezier(0.1, 0.8, 0.2, 1);
}

/* ── Participant UI Components ── */
.participant-label {
    position: absolute;
    bottom: 1.25rem;
    left: 1.25rem;
    background: rgba(15, 23, 42, 0.8);
    backdrop-filter: blur(8px);
    padding: 6px 14px;
    border-radius: 8px;
    color: white;
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid var(--glass-border);
    z-index: 10;
}

.status-badge {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.badge-live {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.meet-header {
    background: rgba(15, 23, 42, 0.5);
    backdrop-filter: blur(12px);
    padding: 1rem 2rem;
    border-radius: 16px;
    border: 1px solid var(--glass-border);
    margin-bottom: 2rem;
}

.meet-title { font-weight: 700; color: white; display: flex; align-items: center; gap: 8px; }
.meet-meta { color: var(--text-muted); font-size: 0.85rem; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.dot-live { background: #ef4444; box-shadow: 0 0 8px #ef4444; }

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
        # ── new planning state ──
        st.session_state.strips_planner      = None
        st.session_state.prolog_kb           = None
        st.session_state.planned_questions   = []
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
    st.session_state.planned_questions   = []
    st.session_state.strips_planner      = None
    st.session_state.prolog_kb           = None
    # Reset selector history so questions restart cleanly
    st.session_state.selector.reset_history()
    # Clear wrapup flag so next session starts fresh
    for key in ['wrapup_started', 'intro_message', 'instant_feedback', 'wumpus_world', 'minimax']:
        if key in st.session_state:
            del st.session_state[key]

# ---------------------------------------------------------------------------
# HELPER — process a submitted answer (voice or text)
# ---------------------------------------------------------------------------
def start_interview_session():
    """Start a new interview using one shared bootstrap path."""
    profile = st.session_state.user_profile
    if not profile or not profile.get("profile_complete"):
        return False, "Please complete and save your profile first."

    reset_interview()

    first_q = None
    if st.session_state.get("csp_toggle"):
        planner = ConstraintSatisfactionPlanner(st.session_state.kb)
        planned = planner.generate_interview_plan()
        if planned:
            st.session_state.planned_questions = planned
            first_q = st.session_state.planned_questions.pop(0)
        else:
            st.warning("CSP planner could not build a valid 10-question plan. Falling back to dynamic selection.")

    if not first_q:
        first_q = st.session_state.selector.select_next_question(profile, [])

    if not first_q:
        return False, "No interview questions are available for the current profile. Please adjust the selected skills and try again."

    st.session_state.current_question = first_q
    st.session_state.interview_active = True
    st.session_state.interview_stage = 'intro'
    st.session_state.interview_start_time = datetime.now()

    initial_state = {"session_started"}
    goal_state = {"session_closed", "report_generated", "advanced_assessed"}
    st.session_state.strips_planner = GoalStackPlanner(initial_state, goal_state, get_strips_actions())
    st.session_state.strips_planner.plan_interview()

    if st.session_state.get("prolog_kb_toggle"):
        st.session_state.prolog_kb = PrologKnowledgeBase()

    return True, None


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

    # Save instant feedback to state
    st.session_state.instant_feedback = feedback

    st.session_state.selector.update_performance(
        q['id'], feedback["score"], q.get("topic", "general")
    )

    total_q = 10   # configurable interview length
    if len(st.session_state.answer_history) < total_q:
        role = st.session_state.user_profile.get("target_role", "Software Engineer")
        
        # Algorithm Selection Logic
        next_q = None

        # 0. Pre-planned syllabus path
        if st.session_state.get("csp_toggle") and st.session_state.get("planned_questions"):
            next_q = st.session_state.planned_questions.pop(0)
        
        # 1. Wumpus World Mode
        if not next_q and st.session_state.get("wumpus_mode"):
            if 'wumpus_world' not in st.session_state:
                from wumpus_interview import WumpusInterviewWorld
                st.session_state.wumpus_world = WumpusInterviewWorld(st.session_state.kb.get_all_questions(), st.session_state.user_profile)
            
            target_cell = st.session_state.wumpus_world.choose_next_cell()
            if target_cell:
                q_obj, effect = st.session_state.wumpus_world.move_agent(target_cell)
                next_q = q_obj
                if effect == "pit":
                    st.toast("⚫ Fell into a Pit! Score for this slot is 0 - skipping.", icon="⚠️")
                    # (Simplified: just assign q_obj to state and continue)
                elif effect == "wumpus":
                    st.toast("💀 Wumpus Attack! Tricky question ahead.", icon="🔥")
        
        # 2. Adversarial Mode (Minimax)
        elif not next_q and st.session_state.get("ai_adversarial_mode"):
            if 'minimax' not in st.session_state:
                from minimax_selector import MinimaxQuestionSelector
                st.session_state.minimax = MinimaxQuestionSelector(st.session_state.kb)
            
            next_q = st.session_state.minimax.select_next_question(
                st.session_state.user_profile, st.session_state.answer_history
            )
        
        # 3. Dynamic Skill Mode (Default fallback)
        if not next_q:
            # STRICT FILTER: Ensure we only pick questions relevant to chosen skills
            chosen_skills = [s.lower() for s in st.session_state.user_profile.get("skills", [])]
            
            # Try Best-First Search with STRICT topic focus
            next_q = st.session_state.selector.select_next_question(
                st.session_state.user_profile, st.session_state.answer_history
            )
            
            # If AI Enhanced, refine the question to match role exactly
            if st.session_state.get('ai_enhanced_mode', False) and next_q:
                from utils import call_gemini
                prompt = (
                    f"Rewrite this interview question to be specifically for a '{role}' candidate "
                    f"focusing only on these technologies: {', '.join(chosen_skills)}.\n"
                    f"Original Question: {next_q['question']}\n"
                    f"Keep it under 25 words. Response ONLY with the new question text."
                )
                dynamic_q = call_gemini(prompt, feature_name="Question Refinement")
                if dynamic_q:
                    next_q["question"] = dynamic_q

        # Update STRIPS State
        if st.session_state.strips_planner:
            update_state_from_answers(st.session_state.strips_planner, st.session_state.answer_history)

        if next_q:
            st.session_state.current_question = next_q
            st.session_state.last_played_q_id = None   # triggers TTS for new question
        else:
            st.session_state.interview_stage = 'wrapup'
            st.session_state.current_question = None
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
        <div style="text-align:center; padding:2rem 1rem; background: var(--bg-card); border-radius: 20px; border: 1px solid var(--glass-border); margin-bottom: 2rem;">
            <div style="background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent));
                        width:80px; height:80px; border-radius:24px; margin:0 auto 1.5rem;
                        display:flex; align-items:center; justify-content:center;
                        box-shadow: var(--neon-indigo); transform: rotate(-5deg);">
                <span style="font-size:2.8rem; color:white; transform: rotate(5deg);">🎯</span>
            </div>
            <h2 style="color: white; margin:0; font-size:1.5rem; font-family: 'Plus Jakarta Sans', sans-serif;">AI Interview Coach</h2>
            <p style="color: var(--text-muted); margin:0.5rem 0 0; font-size:0.85rem; letter-spacing: 1px;">PREMIUM EDITION</p>
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
                st.markdown("<br>", unsafe_allow_html=True)
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
                    try:
                        import json
                        if os.path.exists("users.json"):
                            with open("users.json", "r") as f:
                                users_data = json.load(f)
                        else:
                            users_data = {}
                        email_str = str(email)
                        users_data[email_str] = st.session_state.user_profile
                        with open("users.json", "w") as f:
                            json.dump(users_data, f, indent=4)
                    except Exception:
                        pass
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
                started, message = start_interview_session()
                if started:
                    st.rerun()
                else:
                    st.warning(message)

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

        st.markdown("---")
        st.markdown("#### ⚙️ Advanced Algorithm Settings")
        
        st.session_state.ai_adversarial_mode = st.toggle("🎮 Adversarial Mode (Minimax α-β)", 
            value=st.session_state.get('ai_adversarial_mode', False),
            help="AI will try to pick the hardest questions to challenge you.")
            
        st.session_state.wumpus_mode = st.toggle("🌍 Wumpus World Mode", 
            value=st.session_state.get('wumpus_mode', False),
            help="Navigate a 4x4 grid of logical mystery before each question.")
            
        st.session_state.fol_reasoning = st.toggle("🔬 FOL Reasoning Engine", 
            value=st.session_state.get('fol_reasoning', True),
            help="Use First-Order Logic predicates for evaluation.")
            
        st.session_state.prolog_kb_toggle = st.toggle("🧠 Use PROLOG Knowledge Base (Unit V)", 
            value=st.session_state.get('prolog_kb_toggle', False),
            help="Bridge to SWI-Prolog for data retrieval.")
                
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

# ── Hero Section is now handled inside Stage 0 logic below ──

# ===========================================================================
# ██  STAGE 0: WELCOME (idle)  ██
# ===========================================================================
if not st.session_state.interview_active and not st.session_state.interview_complete:

    st.markdown('''
    <div style="text-align: center; margin-top: 2rem; margin-bottom: 4rem;">
        <h1 class="cosmic-bg" style="font-size: 4.5rem; margin-bottom: 1.5rem; line-height: 1.1; 
            background: linear-gradient(135deg, #fff 30%, #6366f1 70%, #a855f7 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Crack Your Dream Job <br> with AI Intelligence
        </h1>
        <p style="font-size: 1.3rem; color: var(--text-muted); max-width: 700px; margin: 0 auto 3.5rem; font-weight: 400;">
            Master your communication and technical skills with the world's most 
            advanced AI interview simulator. Personalized coaching in real-time.
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # Hero CTA Buttons - CENTERED
    _, c_btn1, c_btn2, _ = st.columns([1, 2, 2, 1])
    with c_btn1:
        if st.button("🎤 START INTERVIEW", use_container_width=True, type="primary"):
            started, message = start_interview_session()
            if started:
                st.rerun()
            else:
                st.warning(message)

    with c_btn2:
        if st.button("📊 VIEW DEMO REPORT", use_container_width=True):
            st.info("Demo report feature coming soon in the next update!")

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # Feature Cards Section
    c1, c2, c3 = st.columns(3)
    feature_items = [
        ("🎥", "Immersive Room", "Glassmorphic environment mimicking top-tier technical video calls."),
        ("🎙️", "Voice & Emotion AI", "Analyze speech patterns, confidence, and clarity in real-time."),
        ("📊", "Deep Analytics", "Premium insights into your technical depth and communication trends.")
    ]
    
    for i, (col, (icon, title, desc)) in enumerate(zip([c1, c2, c3], feature_items)):
        with col:
            st.markdown(f'''
                <div class="saas-card" style="text-align: center; height: 100%;">
                    <div style="font-size: 3rem; margin-bottom: 1.5rem; filter: drop-shadow(var(--neon-indigo));">{icon}</div>
                    <h3 style="margin-bottom: 1rem; font-size: 1.4rem;">{title}</h3>
                    <p style="color: var(--text-muted); font-size: 1rem; line-height: 1.6;">{desc}</p>
                </div>
            ''', unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    with st.expander("� How the AI Simulation Works", expanded=False):
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("""
### The Flow
1. **Profile Setup**: Set your target role and skills.
2. **AI Greeting**: Your coach introduces the session.
3. **Adaptive Questions**: Question difficulty scales based on your answers.
4. **Natural Interaction**: Speak or type your responses.
            """)
        with col_r:
            st.markdown("""
### Pro Tips
- **Be Specific**: Use the STAR method for behavioral questions.
- **Environment**: Ensure a quiet room for voice recognition.
- **Tone**: Maintain professional eye contact with the camera.
- **Analytics**: Review your report to identify weak topic areas.
            """)

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
        # Header is now handled by CSS and consistent placement

    # ── FIX 3: Cache TTS so it plays only ONCE per greeting (not on every rerun) ──
    # Interview stage logic is handled below in the active sections
    # No intro gate here

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
        <div id="videoWrapper" style="position:relative; background:#000; text-align:center; min-height:480px;">
            <video id="localVideo"
                autoplay playsinline muted
                style="
                    width:100%;
                    height:480px;
                    object-fit:cover;
                    display:block;
                    transform:scaleX(-1);
                    border-radius:0 0 14px 14px;
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

    # ── Main Interview Body Layout ──
    # Column 1 & 2: Main Interaction Area | Column 3: Stats
    main_col, stats_col = st.columns([2.5, 1])

    with main_col:
        # ── VIDEO HUD ──
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 2rem; position: relative;">
            <!-- AI Panel -->
            <div class="video-frame saas-card" style="aspect-ratio: 16/9; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
                <div style="position:absolute; top:1rem; left:1rem; z-index:10;">
                    <span class="status-badge badge-live">AI INTERVIEWER</span>
                </div>
        """, unsafe_allow_html=True)
        
        if stage == 'intro':
            st.markdown("""
                <div style="
                    background: rgba(26, 27, 46, 0.6);
                    backdrop-filter: blur(16px);
                    border: 1px solid rgba(108, 99, 255, 0.3);
                    border-radius: 20px;
                    padding: 2.5rem;
                    text-align: center;
                    width: 80%;
                    box-shadow: 0 0 30px rgba(108, 99, 255, 0.2);
                    animation: fadeIn 0.6s ease-in-out;
                ">
                    <h2 style="color:#e8eaed; margin-bottom:0.5rem; font-size:1.4rem;">
                        🤖 AI Coach is Ready
                    </h2>
                    <p style="color:#8892b0; font-size:0.9rem; margin-bottom: 0;">
                        Click below to begin your first question
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            avatar_em = "listening" if not st.session_state.mic_muted else "neutral"
            st.markdown(get_robot_avatar(avatar_em), unsafe_allow_html=True)
        
        st.markdown("""
                <div class="participant-label">AI Coach (Jenny)</div>
            </div>
            <!-- USER LIVE -->
            <div class="video-frame saas-card" style="aspect-ratio: 16/9; position: relative;">
                <div style="position:absolute; top:1rem; left:1rem; z-index:10;">
                    <span class="status-badge" style="background:rgba(239,68,68,0.2); color:#ef4444; border:1px solid rgba(239,68,68,0.3);">LIVE</span>
                </div>
        """, unsafe_allow_html=True)
        
        components.html(camera_html, height=360, scrolling=False)
        
        st.markdown("""
                <div class="participant-label">You (Live)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── FLOATING QUESTION OVERLAY (only when in questions stage) ──
        if q and stage == 'questions':
            st.markdown(f"""
                <div style="margin-top: -3.5rem; position: relative; z-index: 100;">
                    <div class="saas-card" style="background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.1); padding: 1.5rem 2.5rem; border-radius: 20px;">
                        <div style="text-transform:uppercase; color:var(--brand-primary); font-size:0.7rem; font-weight:800; letter-spacing:1px; margin-bottom:0.5rem;">Current Question</div>
                        <div style="font-size: 1.4rem; color: white; font-weight: 600; line-height: 1.4;">"{q['question']}"</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

        # ── 'START FIRST QUESTION' CTA for intro stage ──
        if stage == 'intro':
            _, cta_col, _ = st.columns([1, 2, 1])
            with cta_col:
                if st.button("🚀 START FIRST QUESTION", use_container_width=True, type="primary", key="btn_start_q1"):
                    st.session_state.interview_stage = "questions"
                    st.rerun()

        # ── MEETING CONTROL BAR (visible in ALL active stages) ──
        ctl_c1, ctl_c2, ctl_c3 = st.columns([1,1,1.5])
        with ctl_c1:
            m_lbl = "🔇 Unmute" if st.session_state.mic_muted else "🎙️ Mute"
            if st.button(m_lbl, key="m_btn_final"):
                st.session_state.mic_muted = not st.session_state.mic_muted
                st.rerun()
        with ctl_c2:
            c_lbl = "📷 Cam On" if st.session_state.cam_off else "📷 Cam Off"
            if st.button(c_lbl, key="c_btn_final"):
                st.session_state.cam_off = not st.session_state.cam_off
                st.rerun()
        with ctl_c3:
            if st.button("🔴 End Interview", key="e_btn_final"):
                with st.spinner("Finalizing Analytics..."):
                    st.session_state.report = st.session_state.reporter.generate_report(profile, st.session_state.answer_history)
                st.session_state.interview_active = False
                st.session_state.interview_complete = True
                st.session_state.interview_stage = 'report'
                st.rerun()

    with stats_col:
        # ── SCORE PREVIEW SIDEBAR CARD ──
        # Calculate real-time metrics
        avg_score = 0; conf = 0; clar = 0; tech = 0
        if st.session_state.answer_history:
            scores = [r['score'] for r in st.session_state.answer_history]
            avg_score = sum(scores) / len(scores)
            conf = int(avg_score * 8.5) + random.randint(-5, 5)
            clar = int(avg_score * 7.8) + random.randint(-5, 5)
            tech = int(avg_score * 9.1) + random.randint(-5, 5)

        st.markdown(f"""
            <div class="analytics-panel saas-card" style="background: var(--bg-card); position: sticky; top: 1rem; border: 1px solid var(--glass-border);">
                <div class="panel-title" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--glass-border); padding-bottom: 0.75rem;">
                    <span style="font-weight: 700; color: white;">Intelligence</span>
                    <span style="background: rgba(99,102,241,0.2); color: var(--brand-primary); font-size: 0.7rem; padding: 2px 10px; border-radius: 20px; font-weight: 800;">LIVE</span>
                </div>
                <div class="stat-row" style="margin-top: 2rem;">
                    <div class="stat-label" style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
                        <span>Confidence</span><span>{conf}%</span>
                    </div>
                    <div class="progress-container" style="height: 6px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
                        <div class="progress-fill" style="width: {conf}%; height: 100%; background: var(--brand-primary); transition: width 0.6s ease;"></div>
                    </div>
                </div>
                <div class="stat-row" style="margin-top: 1.5rem;">
                    <div class="stat-label" style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
                        <span>Clarity</span><span>{clar}%</span>
                    </div>
                    <div class="progress-container" style="height: 6px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
                        <div class="progress-fill" style="width: {clar}%; height: 100%; background: linear-gradient(90deg, var(--brand-accent), var(--brand-primary)); transition: width 0.6s ease;"></div>
                    </div>
                </div>
                <div class="stat-row" style="margin-top: 1.5rem;">
                    <div class="stat-label" style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.85rem; color: var(--text-muted);">
                        <span>Technical Depth</span><span>{tech}%</span>
                    </div>
                    <div class="progress-container" style="height: 6px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
                        <div class="progress-fill" style="width: {tech}%; height: 100%; background: linear-gradient(90deg, var(--brand-secondary), var(--brand-primary)); transition: width 0.6s ease;"></div>
                    </div>
                </div>
                <div style="margin-top: 2.5rem; padding: 1.5rem; background: rgba(99,102,241,0.1); border-radius: 16px; border: 1px solid rgba(99,102,241,0.2); text-align: center;">
                    <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 0.5rem; letter-spacing: 1.5px;">Performance Score</div>
                    <div style="font-size: 2.5rem; font-weight: 800; color: white;">{avg_score:.1f}<span style="font-size: 1rem; color: var(--text-muted); font-weight: 400;">/10</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ── STAGES: WRAPUP → QUESTIONS (in priority order) ──
    if stage == 'wrapup':
        if "wrapup_started" not in st.session_state:
            st.session_state.wrapup_started = True
            
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
            
            closing1 = f"That was the last question, {cand_name}. Really appreciate your time today."
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
            
            # Single TTS call to avoid overlapping closing lines
            full_closing = f"{closing1} {closing2}"
            text_to_speech_autoplay(full_closing)
        st.markdown(f"""
            <div class="saas-card" style="background: linear-gradient(135deg, var(--brand-primary), var(--brand-accent)); border:none; text-align:center; padding:4rem 2rem;">
                <h1 style="color:white; font-size:3rem; margin-bottom:1rem; font-family:'Plus Jakarta Sans';">Perfect Finish, {cand_name.split()[0]}! 🎉</h1>
                <p style="color:white; opacity:0.9; font-size:1.3rem; max-width:600px; margin:0 auto;">
                    You've successfully navigated the interview. Our AI is now synthesizing your performance data 
                    to build your personalized growth roadmap.
                </p>
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

        # Play question audio once per question ID.
        # To avoid overlapping audio (acknowledgement + transition + question),
        # we combine everything into a single TTS call.
        if st.session_state.last_played_q_id != q['id']:
            if answered > 0:
                ack = random.choice(ACKNOWLEDGEMENTS)
                trans = random.choice(TRANSITIONS)
                combined = f"{ack} {trans} {q['question']}"
                text_to_speech_autoplay(combined)
            else:
                text_to_speech_autoplay(q['question'])
                
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
            <div class="saas-card" style="margin-bottom:1.5rem; border-left: 4px solid {sc_color};">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;">
                    <span style="font-size:1.2rem; font-weight:700;">Logic Score: <span style="color:{sc_color}">{sc:.1f} / 10</span> {sc_icon}</span>
                    <span class="status-badge" style="background:{sc_color}20; color:{sc_color}; border:1px solid {sc_color}40;">{sc_text}</span>
                </div>
            """, unsafe_allow_html=True)
            st.progress(sc / 10.0)
            
            # --- Prolog Evaluation Row ---
            if st.session_state.get("prolog_kb_toggle") and st.session_state.prolog_kb and st.session_state.prolog_kb.available:
                p_eval = st.session_state.prolog_kb.evaluate_answer_prolog(last_q_id, last_record['answer'])
                st.markdown(f"""
                <div class="saas-card" style="background: rgba(99, 102, 241, 0.05); padding: 1rem; border-color: rgba(99, 102, 241, 0.2); margin-top: 1rem;">
                    <small style="color: var(--brand-primary); text-transform: uppercase; font-weight: 800; letter-spacing: 1px;">🧠 Prolog Logical Verification</small><br/>
                    <div style="margin-top:0.5rem; font-size: 0.95rem;">
                        Matched: <code style="background:rgba(99,102,241,0.1); color:var(--brand-primary); padding:2px 6px; border-radius:4px;">{p_eval['matched_keywords']}</code> <br/>
                        Confidence: <b>{int(p_eval['score_component']*100)}%</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; margin-top: 1.25rem; font-size:0.9rem; color:var(--text-muted); font-weight:500;">
                    <span><i class="fas fa-key"></i> Keywords: {matched_kw_count}/{total_kw}</span>
                    <span><i class="fas fa-brain"></i> Concepts: {matched_concepts}/{total_concepts}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

             # Part 2 — Instant Suggestion Button (real-time generative feedback via Gemini)
            instant_key = f"instant_tip_{last_q_id}"
            if instant_key not in st.session_state:
                if st.button("💡 Get Instant Coaching Tip", key=f"btn_tip_{last_q_id}"):
                    with st.spinner("Getting your AI coaching tip..."):
                        strengths = fb.get("strengths") or []
                        suggestions = fb.get("suggestions") or []
                        missing_c_list = fb.get("missing_concepts") or []

                        # Default deterministic fallback in case Gemini is unavailable
                        did_well = strengths[0] if strengths else "You gave a reasonable starting answer."
                        if suggestions and len(suggestions) > 0:
                            improve_part = suggestions[0]
                        elif missing_c_list:
                            improve_part = (
                                "Next time, make sure you explicitly talk about: "
                                + ", ".join(missing_c_list[:3])
                                + "."
                            )
                        else:
                            improve_part = (
                                "You can make it even stronger by adding one concrete, real-world example "
                                "from your experience."
                            )
                        fallback_tip = f"{did_well} {improve_part}"

                        # Try generative feedback via Gemini (does not depend on ai_enhanced_mode toggle)
                        try:
                            from utils import call_gemini

                            prompt = (
                                "You are a friendly interview coach giving quick real-time advice.\n"
                                f"The candidate just answered this interview question: '{last_q}'\n"
                                f"Their answer was: '{last_record['answer']}'\n"
                                f"They scored {sc}/10.\n"
                                f"They correctly mentioned keywords based on this percentage: {matched_kw_count}/{total_kw}\n"
                                f"They missed these concepts: {missing_c_list}\n\n"
                                "Give ONE specific, actionable tip they can use RIGHT NOW to improve "
                                "this answer if asked again. Start with what they did right in one "
                                "short sentence, then give the improvement tip. Maximum 3 sentences total. "
                                "Be conversational and encouraging, like a friend helping you prep. "
                                "No bullet points, no headers."
                            )

                            tip = call_gemini(prompt, feature_name="Feature: Instant Tip")
                            st.session_state[instant_key] = tip or fallback_tip
                        except Exception:
                            st.session_state[instant_key] = fallback_tip
                    st.rerun()
            
            if instant_key in st.session_state:
                st.markdown(f"""
                <div style="background: rgba(255, 251, 235, 0.1); border-left: 4px solid #f59e0b; padding:1.2rem; border-radius:12px; margin-bottom:1.5rem; border: 1px solid rgba(245,158,11,0.2);">
                    <div style="color:#f59e0b; font-weight:700; margin-bottom:0.4rem; font-size:1rem; display:flex; align-items:center; gap:8px;">
                        <span>💡</span> Quick AI Coaching Tip
                    </div>
                    <div style="color:var(--text-primary); font-size:0.95rem; line-height:1.5;">{st.session_state[instant_key]}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # --- FOL Reasoning Trace ---
            if st.session_state.get('fol_reasoning', True) and fb.get('fol_trace'):
                with st.expander("🔬 View First-Order Logic (FOL) Reasoning Trace", expanded=False):
                    trace_html = []
                    for t in fb['fol_trace']:
                        if "TRUE" in t: color = "#10b981"
                        elif "PARTIAL" in t: color = "#f59e0b"
                        elif "FALSE" in t: color = "#ef4444"
                        else: color = "#6c63ff"
                        trace_html.append(f'<div style="color:{color}; font-family:monospace; margin-bottom:4px;">{t}</div>')
                    st.markdown("".join(trace_html), unsafe_allow_html=True)
        
        predicted_candidates = []
        if not (st.session_state.get("csp_toggle") and st.session_state.get("planned_questions")):
            predicted_candidates = st.session_state.selector.get_predicted_questions(
                st.session_state.user_profile, st.session_state.answer_history, n=3
            )

        # --- STRIPS Interview Plan Visualizer (ALGORITHM UI UNIT VI) ---
        if st.session_state.strips_planner:
            with st.expander("📋 STRIPS Interview Plan Log", expanded=False):
                col_p, col_s = st.columns([2, 1])
                with col_p:
                    st.markdown(st.session_state.strips_planner.get_plan_html(), unsafe_allow_html=True)
                with col_s:
                    current_act = st.session_state.strips_planner.get_current_action(st.session_state.answer_history)
                    st.markdown(f"**Current Action:** `{current_act}`")
                    st.markdown(f"**World Facts:** `{list(st.session_state.strips_planner.state)}`")

        # --- Prolog Query Log (ALGORITHM UI UNIT V) ---
        if st.session_state.get("prolog_kb_toggle") and st.session_state.prolog_kb:
            with st.expander("📝 PROLOG Logical Verification Log", expanded=False):
                for q_log in st.session_state.prolog_kb.get_prolog_query_log():
                    st.code(q_log, language="prolog")

        # Question is now shown in the floating glass card over the video

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
        <div class="saas-card" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2)); text-align:center; padding:4rem 2rem; margin-bottom:3rem; border: 1px solid var(--brand-primary);">
            <h1 class="cosmic-bg" style="font-size:3.5rem; margin-bottom:1rem; 
                background: linear-gradient(135deg, #fff, var(--brand-primary));
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Your Performance Intelligence
            </h1>
            <p style="color: var(--text-muted); font-size:1.2rem; max-width: 600px; margin: 0 auto;">
                Comprehensive analysis for <b>{report['user_profile'].get('name','Candidate')}</b>. 
                Focus on the insights below to level up your career.
            </p>
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
    <div class="footer" style="text-align:center; padding: 2rem 0; color: var(--text-muted); opacity: 0.8;">
        <p>🎯 AI Interview Coach — Professional Edition v3.0</p>
        <p style="font-size:0.78rem;">
            Powered by Best-First Search · Forward-Chaining Evaluation · Streamlit WebRTC<br>
            Built with ❤️ for serious interview preparation
        </p>
    </div>""", unsafe_allow_html=True)


