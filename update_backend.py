import os

app_path = r'c:\Users\hp\ai-interview_cp\ai-interview-coach\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Profile Saving
old_profile_save = """                    st.session_state.user_profile = {
                        "name": name, "email": email,
                        "target_role": target_role,
                        "experience_level": experience.split("(")[0].strip().lower(),
                        "skills": all_skills, "profile_complete": True,
                        "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }"""

new_profile_save = """                    st.session_state.user_profile = {
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
                        users_data[email] = st.session_state.user_profile
                        with open("users.json", "w") as f:
                            json.dump(users_data, f, indent=4)
                    except Exception:
                        pass"""

if old_profile_save in content:
    content = content.replace(old_profile_save, new_profile_save)

# 2. Add instant feedback state and change question generation logic
# Original process_answer function update
old_process_answer = """    record = {
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
        st.session_state.current_question = None"""

new_process_answer = """    record = {
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
        skills_str = ", ".join(st.session_state.user_profile.get("skills", []))
        role = st.session_state.user_profile.get("target_role", "Software Engineer")
        level_exp = st.session_state.user_profile.get("experience_level", "entry")
        
        # Skill-based dynamic question generation
        if st.session_state.get('ai_enhanced_mode', False):
            from utils import call_gemini
            import random
            
            diff_level = "intermediate"
            if feedback["score"] >= 8: diff_level = "advanced"
            elif feedback["score"] < 5: diff_level = "beginner"
            
            prompt = (
                f"You are an expert technical interviewer evaluating a candidate for {role} at {level_exp} level. "
                f"They have these skills: {skills_str}. "
                f"Generate exactly ONE technical interview question of '{diff_level}' difficulty testing ONE of these skills. "
                f"Respond ONLY with the question text. Do not include answers or formatting."
            )
            dynamic_question = call_gemini(prompt, feature_name="Dynamic Skill Question")
            
            if dynamic_question and len(dynamic_question) > 10:
                next_q = {
                    "id": f"q_{len(st.session_state.answer_history)+1}",
                    "question": dynamic_question,
                    "difficulty": diff_level,
                    "topic": random.choice(st.session_state.user_profile.get("skills", ["general"]))
                }
            else:
                next_q = st.session_state.selector.select_next_question(
                    st.session_state.user_profile, st.session_state.answer_history
                )
        else:
            if st.session_state.get("csp_toggle") and st.session_state.get("planned_questions"):
                next_q = st.session_state.planned_questions.pop(0)
            else:
                next_q = st.session_state.selector.select_next_question(
                    st.session_state.user_profile, st.session_state.answer_history
                )

        st.session_state.current_question = next_q
        st.session_state.last_played_q_id = None   # triggers TTS for new question
    else:
        # All questions done → wrapup stage
        st.session_state.interview_stage = 'wrapup'
        st.session_state.current_question = None"""

if old_process_answer in content:
    content = content.replace(old_process_answer, new_process_answer)
    print("process_answer successfully replaced.")

# 3. Add Instant Feedback UI
# Search for where questions are displayed.
# It's at st.markdown(display_question_card(...))

old_question_display = """    # ── Display the active question ──
    st.markdown(display_question_card(
        answered + 1, 
        get_difficulty_level(q), 
        q.get('topic', 'general'), 
        q['question']
    ), unsafe_allow_html=True)"""

new_question_display = """    # ── Instant Feedback Display ──
    if 'instant_feedback' in st.session_state and st.session_state.instant_feedback:
        fb = st.session_state.instant_feedback
        score = fb.get('score', 0)
        c_color = "#00d4aa" if score >= 7 else "#f59e0b" if score >= 4 else "#ff4757"
        
        st.markdown(f'''
            <div style="background: rgba(15,15,26,0.8); border-left: 5px solid {c_color}; 
                        padding: 1.25rem; border-radius: 12px; margin-bottom: 1.5rem; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.3); animation: slideIn 0.5s ease-out;">
                <h4 style="margin-top: 0; color: {c_color}; font-family: 'Space Grotesk', sans-serif;">
                    ⚡ Instant AI Feedback (Score: {score}/10)
                </h4>
                <p style="color: #e8eaed; margin-bottom: 0.5rem; font-size: 0.95rem;">
                    <b>Strengths:</b> {", ".join(fb.get('strengths', ['Good attempt']))}
                </p>
                <p style="color: #8892b0; margin-bottom: 0; font-size: 0.95rem;">
                    <b>Improvement:</b> {fb.get('weaknesses', ['Try to be more specific.'])[0] if fb.get('weaknesses') else 'Keep it up!'}
                </p>
            </div>
        ''', unsafe_allow_html=True)
        # Clear it so it doesn't show multiple times
        st.session_state.instant_feedback = None

    # ── Display the active question ──
    # Hide the backend prompt to the user, only show the question text.
    st.markdown(display_question_card(
        answered + 1, 
        get_difficulty_level(q), 
        q.get('topic', 'Skill Assessment'), 
        q['question']
    ), unsafe_allow_html=True)"""

if old_question_display in content:
    content = content.replace(old_question_display, new_question_display)
    print("Display logic successfully replaced.")

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("done")
