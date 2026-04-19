import os

app_path = r'c:\Users\hp\ai-interview_cp\ai-interview-coach\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_logic = """        # Hidden internal logic (requested by user)
        # ── Instant Feedback Display (Auto-show) ──
        if 'instant_feedback' in st.session_state and st.session_state.instant_feedback:
            fb = st.session_state.instant_feedback
            score = fb.get('score', 0)
            c_color = "#00d4aa" if score >= 7 else "#f59e0b" if score >= 4 else "#ff4757"
            
            st.markdown(f'''
                <div style="background: rgba(15,15,26,0.8); border-left: 4px solid {c_color}; 
                            padding: 1.25rem; border-radius: 12px; margin-bottom: 1.5rem; 
                            box-shadow: 0 4px 15px rgba(0,0,0,0.3); animation: slideIn 0.5s ease-out;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.8rem;">
                        <h4 style="margin: 0; color: {c_color}; font-family: \\'Space Grotesk\\', sans-serif;">
                            ⚡ Real-Time Feedback (Score: {score}/10)
                        </h4>
                    </div>
                    <p style="color: #e8eaed; margin-bottom: 0.5rem; font-size: 0.95rem;">
                        <b>Strengths:</b> {", ".join(fb.get('strengths', ['Good attempt']))}
                    </p>
                    <p style="color: #8892b0; margin-bottom: 0; font-size: 0.95rem;">
                        <b>Improvement Tip:</b> {(fb.get('weaknesses') or ['Try to be more specific.'])[0]}
                    </p>
                </div>
            ''', unsafe_allow_html=True)
            # Clear it so it doesn't show again until next answer
            st.session_state.instant_feedback = None

        # ── Question card using Utils Helper ──
        diff_level = get_difficulty_level(q)
        st.markdown(display_question_card(
            answered + 1, 
            diff_level.title(), 
            q.get('topic', 'General').title(), 
            q['question']
        ), unsafe_allow_html=True)\n"""

del lines[1405:1440]
lines.insert(1405, new_logic)

with open(app_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
    
print("Replaced lines successfully!")
