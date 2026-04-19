# 🎯 AI Interview Coach — Complete Project Breakdown
### Python · Streamlit · AI/ML · Modular Architecture

---

## 1. 🧠 ALL ALGORITHMS USED

### Algorithm 1 — Best-First Search (Heuristic Search)
- **File:** `question_selector.py` → `QuestionSelector`
- **Unit:** Unit III (Informed Search)
- **Why Used:** To select the *most relevant* next question out of all available ones — not randomly, but intelligently based on the candidate's profile and performance.
- **How it works in THIS project:**
  - All unused questions are collected as candidate nodes.
  - A **4-component weighted heuristic** is computed for each:
    - `relevance` (0.3 weight) — Does the topic match the target role?
    - `difficulty_match` (0.3 weight) — Is difficulty appropriate for experience level?
    - `novelty` (0.2 weight) — Has this question been asked before?
    - `weakness_focus` (0.2 weight) — Does the topic hit a low-scoring subject?
  - Formula: `score = 0.3×relevance + 0.3×difficulty + 0.2×novelty + 0.2×weakness`
  - Questions are sorted by score (highest first) → top question is selected.
- **Result:** Interview adapts in real-time — a candidate weak in Python will keep getting more Python questions.

---

### Algorithm 2 — Forward Chaining (via First-Order Logic Engine)
- **File:** `fol_engine.py` → `FOLEngine`, consumed by `answer_evaluator.py`
- **Unit:** Unit V (Knowledge Representation & FOL)
- **Why Used:** To evaluate how good a candidate's answer is — by checking if it satisfies logical predicates (rules).
- **How it works in THIS project:**
  - Each question in the Knowledge Base has `fol_rules` attached — a list of predicates like `Contains("mutable")`, `Explains("indexing")`, `ExemplifiesCode()`, `IsDetailed(25)`.
  - The `FOLEngine` evaluates each predicate against the user's answer text:
    - `Contains(term)` → checks if the term appears in the answer (returns 1.0/0.5/0.0)
    - `Explains(concept)` → checks if the concept appears near an explaining connector word ("is", "means", "refers to")
    - `ExemplifiesCode()` → uses Regex to detect code patterns (`def`, `class`, `for`, `[]`)
    - `IsDetailed(N)` → checks if the answer has at least N words
    - `Defines(term)` → checks pattern "term is / term means / term refers to"
  - Rules are connected by `AND` (average score) or `OR` (max score).
  - Final score = `GoodAnswer_score × 0.7 + PartialAnswer_score × 0.3`, scaled to 0–10.
- **Result:** A 70-word answer with correct keywords scores much higher than a 5-word vague response.

---

### Algorithm 3 — Breadth-First Search (BFS)
- **File:** `knowledge_base.py` → `explore_topics_bfs()`
- **Unit:** Unit II (Uninformed Search)
- **Why Used:** To traverse the hierarchical Knowledge Base (Topic → Difficulty → Question) level by level — as a tree traversal for generating the "Study Topics" sidebar panel.
- **How it works in THIS project:**
  - The KB is structured as: `Topic → {Difficulty → [Questions]}`.
  - BFS visits nodes level by level: first all Topics, then all Difficulty levels under each topic, then all Questions at each level.
  - Returns a flat ordered list used to render the "Study Topics" expander in the UI sidebar.
- **Result:** The sidebar shows `Python → Beginner → "What is a list?"` in proper BFS traversal order.

---

### Algorithm 4 — Constraint Satisfaction Problem (CSP) + Backtracking
- **File:** `interview_planner_csp.py` → `ConstraintSatisfactionPlanner`
- **Unit:** Unit III (CSP) + Unit V (Backtracking)
- **Why Used:** To pre-generate a *guaranteed-valid* 10-question interview plan that satisfies all difficulty and diversity constraints.
- **How it works in THIS project:**
  - **Variables:** 10 question slots to fill.
  - **Domain:** All questions in the Knowledge Base.
  - **Constraints:**
    - Exactly **4 Beginner** questions
    - Exactly **4 Intermediate** questions
    - Exactly **2 Advanced** questions
    - **Minimum 3 distinct topics** must be covered
    - **No repeated questions**
  - **Backtracking Algorithm (`_backtrack`):**
    1. For each unfilled slot, try questions from the domain.
    2. Check all constraints (Forward Checking style — prune early if a count is exceeded).
    3. If valid, assign and recurse to the next slot.
    4. If the path fails at any point, **backtrack** (remove last assignment, try next).
  - A feasibility pre-check runs first to avoid unsolvable searches.
- **Result:** When the user enables "CSP Mode" in the sidebar, the interview follows this pre-planned sequence guaranteed to be complete and fair.

---

### Algorithm 5 — STRIPS Planning (Goal Stack Planning)
- **File:** `strips_planner.py` → `GoalStackPlanner`
- **Unit:** Unit VI (Planning)
- **Why Used:** To model the entire interview as a formal planning problem — where each stage of the interview is an **action** with preconditions and effects.
- **How it works in THIS project:**
  - **Initial State:** `{session_started}`
  - **Goal State:** `{session_closed}`
  - **STRIPS Actions defined:**

    | Action | Preconditions | Add Effects |
    |---|---|---|
    | `greet_candidate` | `session_started` | `candidate_greeted` |
    | `ask_beginner_question` | `candidate_greeted` | `basics_assessed` |
    | `ask_intermediate_question` | `basics_assessed` | `intermediate_assessed` |
    | `ask_advanced_question` | `intermediate_assessed` | `advanced_assessed` |
    | `remediate_weak_topic` | `weak_topic_identified` | `remediation_done` |
    | `generate_report` | `basics_assessed + intermediate_assessed` | `report_generated` |
    | `close_session` | `report_generated` | `session_closed` |

  - The planner finds the ordered sequence of actions that leads from Initial → Goal State.
  - After each user answer, `update_state_from_answers()` updates the World State (e.g., adds `basics_assessed` when a beginner question is answered).
  - The UI shows this live as a **timeline with ✅/▶️/⏳** markers.
- **Result:** The interview follows a structured plan — the AI knows exactly what stage to act on next.

---

### Algorithm 6 — Minimax with Alpha-Beta Pruning
- **File:** `minimax_selector.py` → `MinimaxQuestionSelector`
- **Unit:** Unit III (Adversarial Search)
- **Why Used:** In "Adversarial Mode", the AI acts as an **opponent** — it picks the question that *challenges the candidate the most*, as if the interviewer wants to find weak spots.
- **How it works in THIS project:**
  - The AI (maximizer) tries to pick the question that leads to the *lowest candidate score*.
  - The candidate (minimizer) is simulated to perform best.
  - Alpha-Beta pruning trims branches that cannot improve the outcome.
- **Result:** Adversarial mode creates a harder, more challenging interview to stress-test the candidate.

---

### Algorithm 7 — Wumpus World (Agent-Based Search)
- **File:** `wumpus_interview.py` → `WumpusInterviewWorld`
- **Unit:** Unit II (Agent-Based World)
- **Why Used:** To model the interview grid as a dangerous world — simulating real-world interview risk (you might get an easy question, or fall into a "Pit" which skips, or encounter the "Wumpus" — an extra-hard question).
- **How it works in THIS project:**
  - A grid of interview "cells" is created, each mapped to a question.
  - Some cells contain **Pits** (unanswerable/skip) or **Wumpus** (extremely hard question).
  - The agent uses **percepts** (breezes near pits, stench near wumpus) to decide where to move next.
- **Result:** Adds game-like uncertainty and difficulty variance to the interview flow.

---

## 2. ⚙️ BACKEND ARCHITECTURE

### File-by-File Role

| File | Role |
|---|---|
| `knowledge_base.py` | **The Brain** — stores all questions, FOL rules, keywords, ideal answers in a nested dict (Topic → Difficulty → Questions). |
| `question_selector.py` | **The Intelligence** — uses Best-First Search to pick the next optimal question per user profile. |
| `answer_evaluator.py` | **The Judge** — passes user answers through FOL Engine rules to produce a scored, annotated result. |
| `fol_engine.py` | **The Logic Core** — implements first-order logic predicates (Contains, Explains, ExemplifiesCode, IsDetailed, Defines). |
| `interview_planner_csp.py` | **The Planner** — generates a 10-question plan satisfying hard constraints via CSP + Backtracking. |
| `strips_planner.py` | **The Scheduler** — models the interview as a STRIPS planning problem, tracking real-time world state. |
| `performance_report.py` | **The Analyst** — aggregates all answer scores, generates topic breakdowns, success rates, and improvement suggestions. |
| `utils.py` | **The Toolbox** — provides TTS (Text-to-Speech), STT (Speech-to-Text), typing animations, avatar HTML, Gemini API wrapper. |
| `app.py` | **The Orchestrator** — Streamlit UI that ties all modules together, manages session state, renders the interview room. |

### Complete Data Flow

```
User Input (Profile: Name, Role, Skills, Experience)
    ↓
KnowledgeBase.get_questions_by_topic(skill, level)
    ↓
QuestionSelector._calculate_heuristic() ← Best-First Search
    ↓
Current Question displayed in floating glass card
    ↓
User submits Answer (Voice → STT → Text, OR Typed Text)
    ↓
AnswerEvaluator.evaluate_answer(q_id, answer_text)
    ↓
FOLEngine.evaluate_rule(good_rule) + FOLEngine.evaluate_rule(partial_rule)
    ↓
score = (good × 0.7) + (partial × 0.3) × 10  →  stored in answer_history
    ↓
QuestionSelector.update_performance() → adjusts next question selection
    ↓
STRIPSPlanner.update_state_from_answers() → advances planning state
    ↓
Next question selected (loop) OR wrapup triggered after 10 answers
    ↓
PerformanceReport.generate_report() → full analytics
    ↓
Report Dashboard rendered (charts, scores, recommendations)
```

---

## 3. 🗄️ DATABASE / STORAGE

### What is Used
- **Pure In-Memory Storage** via Streamlit `session_state`
- No files written to disk. No external DB. Everything lives in browser session memory.

### What is Stored

| Data | Storage Key | Type |
|---|---|---|
| User Profile (name, email, role, skills) | `st.session_state.user_profile` | `dict` |
| All answered questions + scores | `st.session_state.answer_history` | `list[dict]` |
| Asked question IDs | `st.session_state.question_history` | `list[int]` |
| Current active question | `st.session_state.current_question` | `dict` |
| Final performance report | `st.session_state.report` | `dict` |
| Planning state (STRIPS facts) | `strips_planner.state` | `set[str]` |

### Limitations
- ❌ Data is **lost on page refresh**
- ❌ No multi-user support (one session per browser)
- ❌ No history between sessions (cannot resume)
- ❌ Knowledge Base is hardcoded in Python — not editable via UI

### Better Alternatives
| Upgrade | Technology | Benefit |
|---|---|---|
| User Profiles | **PostgreSQL** | Persistent login, past sessions |
| Question Bank | **MongoDB** | Dynamic CRUD, easy admin panel |
| Answer Logs | **Firebase/MongoDB** | Real-time sync, analytics |
| Reports | **Redis Cache** | Fast retrieval for dashboards |
| Auth | **Auth0 / Supabase** | Multi-user SaaS ready |

---

## 4. 🚀 FEATURES IMPLEMENTED

### A. Core Features

| Feature | Description |
|---|---|
| Adaptive Interview System | 10-question dynamic interview adapts per profile |
| Best-First Question Selection | Picks hardest/most relevant unseen question |
| FOL Answer Evaluation | Logic-based scoring of natural language answers |
| Performance Report Generation | Topic-wise breakdown, scores, recommendations |
| Session Management | Full state machine (`idle → intro → questions → wrapup → report`) |

### B. Advanced AI Features

| Feature | Description |
|---|---|
| Google Gemini Integration | Dynamic question regeneration, AI coaching tips, LLM session summaries |
| Voice Input (STT) | `audio_recorder_streamlit` + Whisper/Google STT for speech answers |
| Voice Output (TTS) | `edge-tts` speaks questions aloud, acknowledgements, transitions |
| Instant Coaching Tips | Per-question "💡 Get Coaching Tip" powered by Gemini |
| AI-Enhanced Mode | Gemini rewrites questions to match exact role + skills |
| Adversarial Mode | Minimax selector to make the interview maximally challenging |
| Wumpus World Mode | Agent-based question selection with uncertainty/risk |
| CSP Pre-Planning | Generate guaranteed fair 10-question plan before interview |
| STRIPS Live Tracking | Real-time planning state shown as timeline in UI |
| FOL Trace View | See exactly which predicates passed/failed for each answer |
| PROLOG Query Log | View raw logical verification queries per answer |

### C. UI/UX Features

| Feature | Description |
|---|---|
| 2-Panel Video HUD | AI Interviewer (Jenny avatar) + User Live Camera side-by-side |
| Floating Question Overlay | Glass-blur card showing current question over video |
| Live Intelligence Sidebar | Real-time Confidence/Clarity/Technical Depth % meters |
| Performance Score Widget | Running average score displayed as large `X.X/10` |
| Progress Dots | 10 colored dots tracking answered questions (🟢🟡🔴) |
| Mic Toggle | Mute/Unmute with icon change and visual warning |
| Camera Toggle | Camera On/Off with live browser `getUserMedia()` |
| Glassmorphism Design | Full dark cosmic theme with blur panels and neon accents |
| Smooth Animations | Fade-in, slide-up, pulse for interactive elements |
| Algorithm Expanders | STRIPS plan and PROLOG logs available in collapsed expanders |

---

## 5. 🔄 COMPLETE SYSTEM FLOW

```
STEP 1 — PROFILE SETUP
User fills: Name, Email, Target Role, Experience Level, Skills (Languages + Frameworks)
→ Saved to st.session_state.user_profile
→ Sidebar unlocks "START INTERVIEW"

STEP 2 — SESSION INITIALIZATION
"START INTERVIEW" clicked:
→ Engines initialized: KnowledgeBase, QuestionSelector, AnswerEvaluator, Evaluator
→ CSP Planner generates 10-question plan (if enabled)
→ STRIPS Planner initialized with initial_state = {session_started}
→ First question selected via Best-First Search
→ interview_stage = 'intro'

STEP 3 — INTRO STAGE
"🤖 AI Coach is Ready" glassmorphic panel shown
TTS reads welcome message
User clicks "🚀 Start First Question"
→ interview_stage = 'questions'

STEP 4 — QUESTION STAGE (repeats 10 times)
- Floating glass card shows current question
- TTS speaks the question
- Progress dot for current question pulses blue
- User records voice OR types text answer
- Submit triggered → process_answer(answer_text) called

STEP 5 — ANSWER EVALUATION
- FOLEngine checks: Contains(), Explains(), ExemplifiesCode(), IsDetailed()
- GoodAnswer rule score × 0.7 + PartialAnswer rule score × 0.3
- Score scaled to 0–10, saved to answer_history
- Logic Score card shown with color (🟢 ≥7, 🟡 ≥5, 🔴 <5)
- Matching keywords + concepts shown
- Optional: "💡 Get Coaching Tip" fetches Gemini feedback
- QuestionSelector.update_performance() adjusts next question selection
- STRIPS state updated from answer difficulty

STEP 6 — NEXT QUESTION
- Best-First Search re-runs with updated profile + history
- Weakness topics get higher heuristic score → more frequent questions
- TTS speaks: "Got it. Moving on. Next question: ..."
- Repeat STEP 4–5 until 10 answers recorded

STEP 7 — WRAPUP
- interview_stage = 'wrapup'
- Strongest topic calculated from answer averages
- TTS delivers personalized closing message
- "Perfect Finish! 🎉" screen displayed

STEP 8 — REPORT GENERATION
- PerformanceReport.generate_report() aggregates:
  - Overall average score
  - Per-topic breakdown
  - Weak topics identified
  - Answer history timeline
- Full dashboard rendered:
  - Radar chart (topic vs score)
  - Bar chart (question progression)
  - Recommendations
  - LLM-generated summary (if AI mode on)
- User can restart with NEW INTERVIEW
```

---

## 6. 💡 DESIGN DECISIONS

### Why These Algorithms?

| Choice | Reason |
|---|---|
| **Best-First Search** over Random | Random selection wastes time on irrelevant topics. BFS ensures each question has maximum educational impact. |
| **FOL over simple keyword matching** | Keyword matching just checks if a word exists. FOL checks if it's *explained*, *exemplified*, and *detailed* — much closer to how a human evaluator thinks. |
| **CSP + Backtracking** for planning | Guarantees the interview plan satisfies all difficulty constraints — impossible with greedy or random approaches. |
| **STRIPS** over hardcoded flow | STRIPS makes the interview plan *declarative* — you define goals and preconditions, the system figures out the sequence. Easy to extend with new stages. |
| **In-memory storage (session_state)** | Eliminates infrastructure complexity for a prototype. No server setup, no DB connections — ideal for a rapid academic demo. |
| **Streamlit** over Flask/Django | Streamlit renders complex UI with Python alone — zero HTML/CSS needed for core components, perfect for AI demos. |

### How It Scales to Real SaaS

1. **Auth Layer** → Add Firebase Auth / Auth0 for user login
2. **Database** → Store users, sessions, answers in PostgreSQL/MongoDB
3. **Question Bank** → Move to MongoDB with admin CRUD UI
4. **AI** → Upgrade Gemini integration to full conversational session
5. **Resume** → Load previous sessions, track progress over time
6. **Multi-tenant** → Per-company custom question banks
7. **Analytics** → Aggregate data across thousands of candidates

---

## 7. 🎯 FINAL SUMMARY (FOR VIVA)

> *"I built AI Interview Coach — a full-stack AI-powered mock interview system using Python and Streamlit.*
>
> *The core system uses **Best-First Search** to adaptively select the most relevant interview question based on the candidate's role, skills, and current weakness profile. Answers are evaluated using a **First-Order Logic (FOL) engine** that checks logical predicates like keyword presence, conceptual explanation depth, and code examples — giving a score from 0 to 10.*
>
> *The interview structure is planned using a **STRIPS Goal Stack Planner** which tracks what has been assessed and what remains. A **CSP with Backtracking** ensures the pre-generated plan always satisfies difficulty and diversity constraints.*
>
> *For advanced modes, **Minimax** makes the AI adversarial, and a **Wumpus World** agent adds uncertainty-based question selection. **Google Gemini** provides generative question refinement and real-time coaching tips.*
>
> *The UI is built with Glassmorphism design — a 2-panel video HUD with a live camera, floating question overlay, and a Live Intelligence sidebar — all running in a single-page Streamlit app."*
