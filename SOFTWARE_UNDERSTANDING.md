# 📄 Software Understanding: Deep Technical Overview
This document serves as an exhaustive, line-by-line foundational guide designed for a 1st-year Computer Science student.
================================================================================




## 1. 🧭 What Is This App? (Plain English Overview)

Imagine you have a big job interview coming up, and you are very nervous. You want to practice, but your friends are busy, and hiring a professional coach is expensive. This application acts like a friendly, automated, virtual robot coach that sits on your computer and practices interviewing you. It turns on your webcam so you can see yourself (just like in a real Zoom or Google Meet interview), asks you questions out loud using a computer-generated voice, and listens to your answers through your microphone. 

Instead of just recording you, this virtual coach is secretly analyzing everything you say in real-time. It checks if you mentioned the right keywords, understood the main ideas, and provided good examples. After asking you a set number of questions, it hands you a detailed "report card." This report card tells you what you are good at, what you need to study more, and even gives you a step-by-step study plan to get better. It does all of this completely automatically, using logical rules and search algorithms (classic Artificial Intelligence) without needing a human to grade you.





















## 2. 🗂️ How Is The App Structured? (File Map)
This software is broken down into several modular pieces. Think of it like a restaurant. Let's look at every file:

### 📄 `app.py`
- **What is its job?** This is the main orchestrator. It creates the visual user interface (UI) using a library called Streamlit. It handles buttons, text boxes, and connecting your camera.
- **What would break?** If deleted, the user has no way to see or interact with the app. The screen would be blank.
- **Real-world analogy:** app.py is like the restaurant's dining area and the waiter. It takes your order (input) and serves your food (the interview).





### 📄 `knowledge_base.py`
- **What is its job?** This stores all the possible questions, difficulty levels, and the 'ideal' perfect answers.
- **What would break?** If deleted, the app would not know what to ask you. It would have no questions.
- **Real-world analogy:** knowledge_base.py is like a textbook or the restaurant's menu. It holds all the information.





### 📄 `question_selector.py`
- **What is its job?** This file decides *which* question to ask you next based on how well you are doing.
- **What would break?** If deleted, the app would crash when trying to find the next question. It wouldn't know how to pick.
- **Real-world analogy:** question_selector.py is like a smart teacher who realizes you are struggling with addition, so they give you easier questions instead of moving to multiplication.





### 📄 `interview_planner_csp.py`
- **What is its job?** This is an alternative way to pick questions by planning the whole interview in advance using constraints (like exactly 4 easy, 4 medium, 2 hard questions).
- **What would break?** If deleted, the 'Pre-Planned Syllabus' toggle in the UI would break, though the normal dynamic selection would still work.
- **Real-world analogy:** interview_planner_csp.py is like a physical trainer who writes down your exact workout plan for the day before you even step into the gym.





### 📄 `answer_evaluator.py`
- **What is its job?** This file reads what you said and grades it logically against the perfect answer from the knowledge base.
- **What would break?** If deleted, you would answer questions but never get a score or feedback.
- **Real-world analogy:** answer_evaluator.py is like a grader with a rubric, checking off boxes if you mention the right things.





### 📄 `performance_report.py`
- **What is its job?** After the interview is done, this file looks at all your scores and generates charts, strengths, weaknesses, and an A* optimal learning path.
- **What would break?** If deleted, the interview would end abruptly with no summary or feedback report.
- **Real-world analogy:** performance_report.py is like your final end-of-semester report card from the principal.





### 📄 `learning_path_astar.py`
- **What is its job?** This file does the heavy lifting for the performance report. It calculates the fastest way for you to study to reach 'mastery' in your weak topics.
- **What would break?** If deleted, the optimal study plan generation would fail and default to generic advice.
- **Real-world analogy:** learning_path_astar.py is like a GPS navigation system (like Google Maps) but for studying instead of driving.





### 📄 `utils.py`
- **What is its job?** This holds small helper tools: formatting UI boxes, making the robot avatar, giving animations, and turning text into voice or voice into text.
- **What would break?** If deleted, the app would lose its voice, its ability to hear you, and all its pretty animations.
- **Real-world analogy:** utils.py is like the restaurant's toolbox (forks, knives, napkins, light switches) — small things that make the experience work.





### 📄 `requirements.txt`
- **What is its job?** A simple text list of other people's code (libraries) our app needs to run.
- **What would break?** If deleted, your computer wouldn't know what to install to make the app work.
- **Real-world analogy:** requirements.txt is like a grocery shopping list for the computer.





### 📄 `run.bat`
- **What is its job?** A quick script for Windows users to double-click and launch the app easily.
- **What would break?** If deleted, users would just have to type the launch command manually in the terminal.
- **Real-world analogy:** run.bat is like the engine start button on a car.

























## 3. 🚀 Step-by-Step: What Happens When You Launch The App
When you type `streamlit run app.py` into your terminal, a massive chain reaction starts:

1. The Python interpreter reads `app.py` from top to bottom.


2. It sees `import streamlit as st` and loads the web framework into your computer's RAM (memory).


3. It imports all our backend logic classes (`KnowledgeBase`, `QuestionSelector`, etc.).


4. Streamlit starts a local web server (usually at `http://localhost:8501`).


5. Your default web browser automatically opens a new tab pointing to that local URL.


6. In the browser, Streamlit begins rendering the page. It sets the page title to 'AI Interview Coach' and applies our custom CSS (colors, rounded corners).


7. The app checks if a `session_state` exists. Since this is a fresh launch, it is empty.


8. The `init_session_state()` function runs. It creates instances (objects) of our backend classes and stores them in memory so they aren't lost when you click a button.


9. Wait, what is `session_state`? It's like a backpack the app wears. Every time the page refreshes (which Streamlit does on EVERY button click), it looks in the backpack to remember what was going on. It puts `interview_active = False` in the backpack.


10. The browser draws the wide layout: The left sidebar asks for your User Profile. The main area shows the Welcome Screen with three big feature boxes.


11. The app finishes loading. It is now patiently waiting for the user to type in their name and click a button.






















## 4. 👤 User Profile — What Does The User Enter and Where Does It Go?
Before starting, the user must define who they are and what job they want.

**Input Fields Shown:**
- **Full Name** (Text box): Any string, e.g., 'Alice Smith'
- **Email** (Text box): Any valid email, e.g., 'alice@example.com'
- **Target Role** (Dropdown): Options like 'Software Engineer', 'Data Scientist', 'Frontend Developer', etc.
- **Experience Level** (Radio Buttons): 'Entry Level (0-2 years)', 'Mid Level (3-5 years)', etc.
- **Skills (Languages, Databases, Frameworks, Tools)** (Multi-select boxes): Python, SQL, React, AWS, etc.

**Where is this data stored?**
```python
st.session_state.user_profile = {
    'name': 'Alice Smith', 
    'email': 'alice@example.com',
    'target_role': 'Software Engineer',
    'experience_level': 'entry',
    'skills': ['Python', 'SQL', 'Git'],
    'profile_complete': True
}
```

**How is it used later?**
1. **Greeting:** The AI voice uses `name` to say 'Hello Alice Smith, welcome to your interview for Software Engineer.'
2. **Question Selection:** If target role is 'Data Scientist', the selector will prioritize asking 'SQL' and 'Python' questions instead of HTML/CSS.
3. **Difficulty Matching:** If experience is 'entry', the app starts by asking 'beginner' questions.

**How could this be improved?**
In the future, we could add a 'Resume Upload' field where a user uploads a PDF. We could use Natural Language Processing (NLP) to parse their exact past projects and generate hyper-specific questions about their unique resume bullet points.








































## 5. 🧠 The Knowledge Base — Where Are The Questions Stored?
The `knowledge_base.py` file contains a giant dictionary (a structured key-value mapping) that holds all data.

### Data Structure Tree
```text
[ROOT]
 ├── python
 │    ├── beginner
 │    │    ├── Q1: What is a list?
 │    │    ├── Q2: Tuple vs List?
 │    │    └── Q3: If-else example?
 │    ├── intermediate
 │    │    ├── Q4: Decorators?
 │    │    └── Q5: List comprehensions?
 │    └── advanced
 │         ├── Q6: Generators?
 │         └── Q101: Metaclasses?
 ├── sql
 │    ├── beginner 
 │    │    ├── Q7: What is SQL?
 │    │    └── Q8: SELECT statement?
 │    ├── intermediate
 │    │    └── Q9: JOINs?
 │    └── advanced
 │         └── Q102: Window functions?
 ├── dsa
 │    ├── beginner
 │    │    └── Q10: Arrays?
 │    ├── intermediate
 │    │    └── Q11: Binary Search?
 │    └── advanced
 │         └── Q103: Dynamic Programming?
 └── javascript
      └── beginner
           └── Q12: Difference from Java?
```

### Complete Example Question Object
```python
{
    'id': 1,
    'question': 'What is a list in Python?',
    'topic': 'python',
    'difficulty': 'beginner',
    'difficulty_level': 'beginner',
    'keywords': ['mutable', 'ordered', 'sequence', 'collection', '[]'],
    'concepts': ['mutable', 'indexing', 'slicing']
}
```
**Field Explanations:**
- `id`: A unique number. Used so we don't accidentally ask you the same question twice.
- `question`: The actual text the robot AI will speak aloud to you.
- `topic` & `difficulty`: Categorization labels so the algorithm knows what bucket this belongs to.
- `keywords`: Important vocabulary words. If you say 'mutable', the grader gives you points.
- `concepts`: Deeper ideas you must explain. Later, the evaluator checks if your answer is long enough around these topics to prove you aren't just guessing keywords.

**Stats:**
- Total Topics: 4
- Difficulty Levels: 3
- Total Questions Hardcoded: 15 questions.








































## 6. 🔍 BFS Knowledge Explorer — How Does It Work?
Breadth-First Search (BFS) is a classic computer science algorithm for traversing (exploring) a tree structure. Imagine spilling water on the top of a pyramid. The water naturally covers the entire top layer, then drips down to cover the entire second layer, and so on. It searches broadly across a level before going deeper. In plain English for a 10-year-old: BFS is like exploring a 3-story house by checking every single room on the 1st floor before you are allowed to walk up the stairs to the 2nd floor.

**How it applies to our tree:**
Our tree levels are: Level 0 (Root) -> Level 1 (Topics) -> Level 2 (Difficulties) -> Level 3 (Questions). BFS ensures we list ALL topics first, then ALL difficulties, then ALL questions, guaranteeing an organized list.

**Trace Example (Using a Queue):**
A 'Queue' is a line at a grocery store. First In, First Out (FIFO).
```text
Step 1: Queue = [ ROOT ]
Step 2: Pop ROOT. It has 4 children (Python, SQL, DSA, JS). Add them to Queue.
        Queue = [ Python, SQL, DSA, JS ]
Step 3: Pop Python. Add its children. 
        Queue = [ SQL, DSA, JS, Beg_Python, Int_Python, Adv_Python ]
Step 4: Pop SQL. Add its children.
        Queue = [ DSA, JS, Beg_Python, Int_Python, Adv_Python, Beg_SQL, Int_SQL, Adv_SQL ]
... 
Step N: Eventually all topics and difficulties are popped, leaving only Questions in the queue.
        Queue = [ Q1, Q2, Q3, Q4... ]
```

**Where does the user see this?**
In `app.py`, there is an expander in the left sidebar called '📚 Study Topics'. Opening it dumps out the BFS array so the user can study the exact syllabus.

**Why BFS instead of DFS?**
DFS (Depth-First Search) dives to the bottom immediately. It would show Root -> Python -> Beginner -> Q1 -> Q2. This is useful for finding a specific path, but to give a broad 'Explorer' view of the syllabus categorizations layer by layer, BFS structures the data visually much better.








































## 7. 🎯 Question Selection — How Does The App Decide What To Ask Next?
We have two completely different algorithms that can pick questions. The user can toggle between them. Here is how they both work.

### Method A: Best-First Search (Dynamic/Default)
Best-First Search is an algorithm that uses a 'Heuristic' (an educated guess or formula) to score all possible options, and then greedily picks the absolute best option right now.

**The Heuristic Formula:**
```python
score = (0.3 * relevance) + (0.3 * difficulty_match) + (0.2 * novelty) + (0.2 * weakness_focus)
```
Every available question runs through this formula and gets a score between 0.0 and 1.0. We sort them, and the question with the highest score wins!

**Inputs to the formula:**
- `relevance`: Does this question's topic match your job? (Data Scientist + SQL = High relevance).
- `difficulty_match`: Are you an 'entry' level looking at a 'beginner' question? (Match = 1.0).
- `novelty`: Have we asked this recently? If yes, penalize it so we don't repeat.
- `weakness_focus`: Did you get a low score on Python previously? If so, give Python questions a bonus multiplier so you are forced to practice your weaknesses! (Note: The selector looks backward through `answer_history` and finds the *most recent* score for each topic. `weakness_focus` is calculated as: `1.0 - (latest_score_for_this_topic / 10.0)`. So if your latest Python score is 2/10 → weakness_focus = 0.8. If your latest Python score is 9/10 → weakness_focus = 0.1. This means the heuristic reacts instantly after every single answer!)

**Real Example Walkthrough:**
Suppose Alice is a Junior Dev. She answers Q1 (Python Beginner) and gets a 2/10 score. The system needs to pick the next question. It evaluates the remaining pool:
- Q2 (Python Beginner): High relevance, High difficulty match, High weakness focus (because she just failed Python). **Score: 0.95**
- Q102 (SQL Advanced): Low relevance, low difficulty match. **Score: 0.21**
- The system automatically selects Q2 to help her practice what she just failed. Yes, the difficulty dynamically changes based on your profile and past answers via this heuristic.

*Note: The system also has a `get_predicted_questions()` method that runs the heuristic scoring on all remaining questions and returns the top 3 candidates WITH their float scores, but does NOT remove them from the queue. It is a "peek" operation used only for the visualizer panel.*





















### Method B: CSP + Backtracking (Pre-Planned Mode)
A Constraint Satisfaction Problem (CSP) is like solving a Sudoku puzzle. You have empty slots, and you must put numbers in them, but you must obey strict rules (constraints).

**The Exact 3 Constraints:**
1. The 10 questions must be EXACTLY: 4 Beginner, 4 Intermediate, 2 Advanced.
2. The questions must span at least 3 distinct topics (e.g. Python, SQL, DSA).
3. No question ID can be repeated.

**What is Backtracking?**
Imagine navigating a complex maze. You walk down a path. Suddenly, you hit a dead end. Instead of staying stuck, you literally walk backwards (backtrack) to the last intersection you passed, and try a different hallway. In code, backtracking assigns a question to a slot, checks if it breaks a rule, and if it does, it removes that question and tries the next one.

**Trace of a Backtrack:**
```text
Slot 1: assigned Q1 (Beginner Python) - OK
...
Slot 4: assigned Q8 (Beginner SQL) - OK
[Wait: We now have 4 Beginner questions]
Slot 5: Algorithm attempts to assign Q10 (Beginner DSA)
Constraint Check: limits['beginner'] >= 4 is TRUE. Rule Violated!
Backtrack: Algorithm rejects Q10, steps back. 
Next attempt for Slot 5: Q4 (Intermediate Python). Rule OK! It continues.
```

**Difference from Method A:** Method A determines the question dynamically *while* you are taking the interview. Method B uses strict mathematical logic to generate the entire 10-question sequence *before* the interview even starts, overriding any dynamic behavior.








































## 8. 🗣️ The Interview Flow — Question By Question
Here is the exact lifecycle of your interview in the application:
1. **First Question:** When you click 'Start', the system queries either the BFS Heuristic or the CSP Planner to get Q1. It saves Q1 to `st.session_state.current_question`.
2. **Introduction:** The state shifts to `stage = 'intro'`. The AI voice greets you, using Google TTS to synthesize an MP3. You press 'Ask First Question'.
3. **Asking:** The state shifts to `stage = 'questions'`. The UI plays the TTS for Q1. The webcam component `getUserMedia` renders your video natively in your browser.
4. **Answering:** You talk into your microphone. The `speech_recognition` module captures your audio clip and converts it to text.
5. **Submission:** You click Submit. Immediately, the string of text is passed into `answer_evaluator.py`. The evaluator grades you instantly (we'll explain how next).
6. **Storage:** The app packages your original text, the AI's feedback, and your score into a dictionary and appends it to `st.session_state.answer_history`. It also flags the Question ID as 'used' so it won't repeat.
7. **Next Step:** The system counts the length of `answer_history`. If it is less than 10, it calls the Question Selector for the next question. The screen refreshes, showing Q2.
8. **Ending:** When `len(answer_history) == 10`, the system forcibly changes the `interview_stage` to `'report'`. The main screen clears out the video and displays your report card.








































## 8.5 🛤️ Question Path Visualizer Panel
This panel exists to make the invisible AI decision-making visible directly on your screen — like showing the GPS route while driving instead of just arriving at the final destination. 

**The Three-Box Visual Timeline:**
- **LEFT box:** The previous question that was just asked, along with the score you got on it (greyed out, done).
- **CENTER box:** The current question being asked right now (highlighted, active).
- **RIGHT box:** The "predicted next question" — what the AI is currently planning to ask you based on your performance so far (shown as a preview, slightly faded). 

The RIGHT box updates live the moment you submit an answer. If you bombed your Python question, a Python question will appear there. If you aced it, a different topic or harder question will appear.

**"🧠 Internal AI Logic" Dropdown:**
Underneath the timeline is a collapsible dropdown that shows the top 3 candidate questions the AI is currently considering, along with their raw heuristic float scores:
  1. "What are Python decorators?" — 0.91 (weakness_focus active)
  2. "Explain SQL JOINs"           — 0.74
  3. "What is recursion?"          — 0.61

Each float score tells you how strongly the AI wants to pick that question. `0.0` means the AI has no interest in this question right now, while `1.0` means the AI considers this the perfect next question based on relevance, novelty, difficulty, and weakness focus.

*Note: This panel is for transparency and demonstration only — the user cannot manually override the AI's choice. We're just lifting the hood so you can watch the engine running!*

## 9. ✅ Answer Evaluation — How Does The App Score Your Answer?
This app does NOT use ChatGPT. It is entirely rules-based, relying on **Forward Chaining**.

**What is Forward Chaining?**
Imagine a doctor trying to diagnose you. They start with facts: 'You have a fever' and 'You have a cough'. They chain these facts forward through medical rules to reach a conclusion: 'You have the flu.' Our app uses your spoken sentences as 'facts' and pushes them through a rules engine to see if they match the 'ideal facts'.

**The Scoring Formula:**
```python
total_score = (keyword_score * 0.4) + (concept_score * 0.4) + (example_score * 0.2)
```
The final score is multiplied by 10 to give a grade out of 10. A score >= 7 is High/Pass. A score 5-6 is Medium. Below 5 is Low/Fail.

**Difference between Keyword and Concept matching:**
- **Keyword matching:** Simple text searching. Did you say the word 'mutable'? If yes, +points. It's very raw string checking.
- **Concept matching:** Much stricter. The system splits your answer into words. It checks if you mentioned the concept (e.g., 'indexing') AND verifies that your surrounding answer is structurally rich (has more than 20 words). It requires context to prove you didn't just rattle off a list of buzzwords.

**Real Example Walkthrough:**
Question: *What is a list in python?*
User Answer: *A list stores items in order.*
- **Facts Extracted by NLP:** ['A list stores items in order']
- **Keyword Score:** Ideal keywords were `['mutable', 'ordered', 'sequence', 'collection', '[]']`. The user said 'order' (matches ordered). So they got 1 out of 5 keywords = 0.2 score. (0.2 * 0.4 weight = 0.08)
- **Concept Score:** Ideal concepts were `['mutable', 'indexing', 'slicing']`. The user mentioned none of these. Score = 0.0.
- **Example Score:** The user provided no code snippet. Score = 0.3 (a harsh default for missing examples).
- **Final Total:** `(0.08 + 0.0 + (0.3*0.2)) * 10 = 1.4 / 10`. The system outputs a very low score and advises the user to mention 'mutability' and add code examples.








































## 10. 📊 Performance Report — How Is The Final Score Calculated?
When you finish, the app loops over your 10 scores and calculates weighted averages. If you scored a 3 and a 9 in Python, your total Python score is 6.0. It renders beautiful interactive charts using `Plotly`.

### The A* Learning Path Algorithm
A* (A-Star) is the crown jewel of search algorithms. It is used in video games and GPS systems to find the absolute shortest path from point A to point B.

**GPS Analogy:**
Imagine driving from New York to LA. You are in Chicago. A* calculates two things: `g(n)` how long it took to get from NY to Chicago, and `h(n)` an estimation of how long it will take from Chicago to LA as the crow flies. It adds them together to get `f(n)`. It always picks the next city that minimizes `f(n)`.

**In our app:**
- **State:** Your scores right now. `{'python': 3, 'sql': 6, 'dsa': 2}`.
- **Goal State:** Every topic scores at least 8.0.
- **g(n):** The actual hours you would spend taking a study module (e.g., spending 1 hour on Python basics).
- **h(n):** The 'Heuristic'. An optimistic guess of how many hours are left. We calculate: sum all your score deficits (e.g., Python needs 5 points) and divide by 2.0 (assuming you learn fast).
- **f(n):** Total score. The algorithm uses a Priority Queue (a waiting line where VIPs skip to the front) to always explore the lowest `f(n)` study plan.

**Trace measuring A* iterations:**
```text
Target Mastery = 8.0.
Start State: Python=3, SQL=6, DSA=2
Deficits = Py(5) + SQL(2) + DSA(6). h(start) = 13 total points / 2 = 6.5 estimated hours.

Iteration 1:
  Applies Module: 'Python Basics' (Cost: 1 hour, Gains: 2 points)
  New State: Py=5, SQL=6, DSA=2
  g(n) = 1.0 hour elapsed.
  h(n) = (3+2+6)/2 = 5.5 hours remaining.
  f(n) = 6.5. Added to Priority Queue.
  Applies Module: 'SQL Select' (Cost: 1 hour, Gains: 2 points)
  New State: Py=3, SQL=8, DSA=2
  g(n) = 1.0 hour elapsed.
  h(n) = (5+0+6)/2 = 5.5 hours remaining.
  f(n) = 6.5. Added to Priority Queue.

Iteration 2:
  The queue pops the lowest f(n) state and repeats applying modules until all scores hit 8.0.
```

**Final Output Example:**
```text
📍 Your Optimal Study Path (A* Search Minimal Path - Total: 12.5 hrs)
1. Python Basics & Variables (1.0 hr)
2. SQL Select & Filtering (1.0 hr)
3. Python Data Structures (1.5 hr)
... etc
```








































## 11. 🎤 Voice System — How Does Speech Work?
The avatar is not just silent text.
- **Speaking (TTS):** We use a library called `gTTS` (Google Text To Speech). The python code takes the question string, sends it to Google's API, and receives a raw MP3 audio file. We encode this MP3 into a base64 string and inject it into `<audio autoplay>` HTML tags in the Streamlit page so it plays instantly.
- **Listening (STT):** We use `audio_recorder_streamlit` to render a mic button on the webpage. When you hit stop, the browser sends your RAW WAV audio bytes to python. Python uses `SpeechRecognition` to decode that WAV file into English text.
- **Fallback:** If the microphone fails or you deny browser permissions, the application does not crash. It catches the network/permission error inside a `try/except` block and safely shows a text-input box so you can type your answer instead.








































## 12. 🗺️ Complete Data Flow Diagram
Here is how data physically moves through the Python files during a session:
```text
[User opens browser] ---> app.py renders UI
       │
       ▼
 [Sidebar Profile] ---> user defines Role/Exp ---> saved in session_state
       │
       ▼
 [Start Clicked] --(requests Q1)--> question_selector.py
                                           │
       (grabs topics & data) <-------------┤ (Reads) knowledge_base.py
                                           │
       (returns Q1 dict) <-----------------┘
       │
       ▼
 [app.py stage='questions'] ---> calls utils.py (TTS) -> robot talks
       │
       ▼
 [User Speaks Answer] ---> STT pipeline converts voice to text
       │
       ▼
 [Text Submitted] ---> answer_evaluator.py (Forward Chaining engine)
                                           │
       (grades via rules) <----------------┤ (Reads Ideal Answer) knowledge_base.py
                                           │
       (returns score + feedback) <--------┘
       │
       ▼
 [Score stored in session_state.answer_history]
       │
       ▼
 [question_selector._calculate_weakness_focus()]
   → scans answer_history for LATEST score per topic
   → computes weakness_focus = 1.0 - (latest_score / 10)
       │
       ▼
 [Best-First Search scores ALL remaining questions]
   → returns top 1 as next question
   → returns top 3 as predicted candidates (peek only)
       │
       ▼
 [Question Path Visualizer Panel updates in UI]
   → LEFT:   previous question + score
   → CENTER: current question
   → RIGHT:  top 1 predicted next question
   → DROPDOWN: top 3 with heuristic float scores
       │
       ▼
 (Loops 10 times)
       │
       ▼
 [Loop Done] ---> array of 10 scores sent to performance_report.py
       │                                     │
       │                                     ▼
       │                          learning_path_astar.py (A* search)
       │                                     │
       ▼                                     ▼
 [app.py stage='report'] <------ (Returns Graphs & Optimal Path)
       │
       ▼
 [Final Output Displayed to User]
```








































## 13. 🔮 Future Improvements (Mapped to Syllabus)
This app is heavily grounded in Classical AI. Here are ideas to expand it using the remaining ML2306 Syllabus concepts that haven't been touched yet:

- **Wumpus World (Unit IV):** We could model the interview room as a Wumpus World grid where the 'Wumpus' is a trick question. The AI agent navigates the grid safely to avoid asking inappropriate or completely irrelevant questions.
- **First-Order Logic (Unit IV):** We could upgrade the Answer Evaluator from simple Forward Chaining to First-Order Logic predicates like `Contains(Answer, 'List') AND IsFaster(Tuple, List)`. This allows much more complex mathematical evaluation rules.
- **PROLOG (Unit V):** We could rewrite the entire `knowledge_base.py` module in PROLOG syntax instead of JSON, allowing the python code to query relations natively using a logic programming bridge (like `pyswip`).
- **STRIPS / Goal Stack Planning (Unit VI):** Instead of picking 1 question at a time, we build an agent with Preconditions and Effects (STRIPS logic) that dynamically plans the physical sequence of 'Introduce self -> Ask Basics -> If Passed -> Ask Coding -> Say Goodbye'.
- **Minimax Game Playing (Unit III):** We could treat the interview as a competitive game. The AI interviewer tries to minimize the candidate's score (by asking the hardest possible legal questions), while the candidate maximizes it, using Alpha-Beta pruning to anticipate user comfort levels.








































## 14. 📚 Glossary
A quick-reference for the technical jargon used throughout this document.

- **Agent:** A computer program that takes actions in an environment to achieve a goal (our interviewer is the agent).
- **State Space:** The map of all possible situations (scores) a user could be in at any given time.
- **Heuristic:** A mathematical 'rule of thumb' or educated guess used to score your options quickly (like our 4-part formula for picking questions).
- **Breadth-First Search (BFS):** An algorithm that searches a tree level-by-level horizontally before going deep vertically.
- **A* Search:** An optimal pathfinding algorithm that adds the actual cost elapsed to the estimated cost remaining to find the fastest route.
- **Constraint Satisfaction Problem (CSP):** A type of math puzzle where you must assign values to variables without breaking strict rules (like Sudoku).
- **Backtracking:** An algorithm strategy where if you hit a dead end breaking a rule, you step backward and try a different option.
- **Forward Chaining:** A logical reasoning method that starts with known facts (what you said) and applies rules to extract a conclusion (your grade).
- **First-In-First-Out (FIFO):** A queue system where the first item added is the first one removed, used primarily in BFS.
- **Priority Queue:** A special line where elements are sorted by a score (priority), so the lowest score always jumps to the front of the line (used in A*).
- **Admissible Heuristic:** A heuristic parameter in A* that never legally over-estimates the true cost to reach the goal, guaranteeing a perfect answer.
- **DOM (Document Object Model):** The HTML architecture of a webpage that dictates where videos and buttons are drawn.
- **getUserMedia:** A web browser command that requests physical permission to turn on your local webcam or microphone.
- **Text-to-Speech (TTS):** Technology that converts written python text strings into spoken audio MP3 files.
- **Speech-to-Text (STT):** Technology that listens to human microphone audio and transcribes it back into python text strings.
- **Base64 Encoding:** A way to convert messy binary data (like an audio file) into a long single string of text so it can be passed through HTML.
- **Session State:** A mechanism in Streamlit that acts like a memory backpack, preventing variables from deleting themselves every time you click a button.
- **Orchestrator:** The main script (like app.py) that acts as the boss, commanding all other smaller helper files when to do their jobs.
- **Dictionary (Dict):** A data structure in Python that maps a 'key' (like 'name') to a 'value' (like 'Alice').
- **Hardcoded:** Data that is written directly inside the python code files rather than pulled dynamically from an external SQL database server or API.
- **weakness_focus:** The component of the Best-First heuristic that boosts priority of topics where your most recent score was low. Calculated as 1 minus your latest normalised score for that topic.
- **get_predicted_questions():** A method that runs the full heuristic scoring and returns the top N candidates without removing them from the question pool. Used exclusively for the visualizer panel.
- **Peek Operation:** Reading the top item of a queue without removing it — like looking at the next card in a deck without drawing it.






