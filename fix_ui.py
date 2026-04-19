import os

app_path = r'c:\Users\hp\ai-interview_cp\ai-interview-coach\app.py'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

old_logic = """        with st.expander("🧠 Internal AI Logic (Top Candidate Questions)"):
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
        st.markdown(f\"\"\"
            <div style="text-align:center; font-size:1.1rem; color:#94a3b8; font-weight:600; text-transform:uppercase; margin-bottom: 0.6rem; margin-top: 1rem;">
                Question {answered + 1} of 10
            </div>
        \"\"\", unsafe_allow_html=True)
            
        st.markdown(f\"\"\"
            <div style="background:white; color:#1e293b; padding:1.8rem; border-radius:14px; text-align:center; box-shadow:0 10px 25px -5px rgba(0,0,0,0.1); border:1px solid #e2e8f0; margin-bottom:1rem;">
                <div style="font-size:20px; font-weight:600; line-height:1.6; margin-bottom:1rem;">{q['question']}</div>
                <div style="display:inline-block; margin-top:0.4rem;">
                    <span class="badge badge-{diff_level}">{diff_level.title()}</span>
                    <span style="font-size:0.8rem; color:#64748b; margin-left:10px;">📌 Topic: {q.get('topic','General').title()}</span>
                </div>
            </div>\"\"\", unsafe_allow_html=True)"""

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
                        <h4 style="margin: 0; color: {c_color}; font-family: 'Space Grotesk', sans-serif;">
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
        ), unsafe_allow_html=True)"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully replaced UI logic!")
else:
    print("String not found. Let's dump a chunk of text to check what's wrong.")
    # finding similar snippet
    start_idx = content.find('with st.expander("🧠 Internal AI Logic')
    if start_idx != -1:
        print("Found expander! The code chunk looks like this:")
        print(content[start_idx:start_idx+1000])
    else:
        print("Couldn't find the internal logic expander.")
