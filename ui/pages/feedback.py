import streamlit as st
import pandas as pd
import json
from datetime import datetime
from ui.components.metrics import render_metric_card
from ui.components.charts import plot_score_trend, plot_topic_performance, plot_difficulty_breakdown

def render():
    if not st.session_state.interview_complete or not st.session_state.report:
        st.session_state.current_page = 'dashboard'
        st.rerun()
        return

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
            <div style="background:rgba(34,197,94,0.1); border-left:5px solid var(--success); padding:1.5rem; border-radius:10px; margin-bottom:1.5rem;">
                <h4 style="color:var(--success); margin-top:0; margin-bottom:0.8rem;">✨ AI Coach Summary</h4>
                <p style="color:var(--text-main); margin:0; font-size:1.1rem; line-height:1.6;">{report['llm_summary']}</p>
            </div>""", unsafe_allow_html=True)

    mc1, mc2, mc3, mc4 = st.columns(4)
    score = report['summary']['overall_score']
    score_color = "var(--success)" if score >= 7 else "var(--warning)" if score >= 5 else "var(--error)"
    perf_level  = report['summary']['performance_level']

    with mc1:
        render_metric_card("⭐", f"<span style='color:{score_color}'>{score}/10</span>", f"Overall · {perf_level.title()}")
    with mc2:
        render_metric_card("📝", str(report['summary']['total_questions']), "Questions Answered")
    with mc3:
        render_metric_card("✅", f"{report['summary']['completion_rate']}%", "Completion Rate")
    with mc4:
        render_metric_card("💪", str(len(report['detailed_analysis']['strongest_topics'])), "Strength Areas")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Summary", "📈 Analytics", "📋 Question Review",
        "📚 Learning Path", "🎯 Recommendations"
    ])

    with tab1:
        st.subheader("📊 Topic-wise Performance")
        plot_topic_performance(report['detailed_analysis']['by_topic'])

    with tab2:
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("📈 Score Progression")
            plot_score_trend(report['detailed_analysis']['progress_over_time'])
        with col_r:
            st.subheader("📊 Difficulty Breakdown")
            plot_difficulty_breakdown(report['detailed_analysis']['by_difficulty'])

        col_s, col_w = st.columns(2)
        with col_s:
            st.subheader("✅ Strengths")
            for s in report['detailed_analysis']['strongest_topics']:
                st.markdown(f"""
                    <div style="background:rgba(16,185,129,0.1);padding:0.9rem;border-radius:10px;margin:0.4rem 0;">
                        <strong style="color:var(--text-main);">{s['topic'].title()}</strong>: {s['score']}/10
                        <br><small class="badge badge-{s['level']}">{s['level'].title()}</small>
                    </div>""", unsafe_allow_html=True)
        with col_w:
            st.subheader("🔧 Areas to Improve")
            for w in report['detailed_analysis']['weakest_topics']:
                st.markdown(f"""
                    <div style="background:rgba(239,68,68,0.1);padding:0.9rem;border-radius:10px;margin:0.4rem 0;">
                        <strong style="color:var(--text-main);">{w['topic'].title()}</strong>: {w['score']}/10
                        <br><small class="badge badge-{w['level']}">{w['level'].title()}</small>
                    </div>""", unsafe_allow_html=True)

    with tab3:
        st.subheader("📋 Detailed Question-by-Question Review")
        if not st.session_state.answer_history:
            st.info("No answers were recorded.")
        else:
            total_qs = len(st.session_state.answer_history)
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
                    st.markdown("---")

    with tab4:
        st.subheader("📚 Personalised Learning Path")
        for phase in report['learning_path']:
            p_color = {"high":"var(--error)","medium":"var(--warning)","low":"var(--success)"}.get(phase['priority'],"var(--primary-color)")
            st.markdown(f"""
                <div style="background:var(--card-bg);padding:1.25rem;border-radius:14px;margin:0.8rem 0;
                            border-left:5px solid {p_color}; border: 1px solid var(--card-border); box-shadow:0 3px 8px rgba(0,0,0,0.06);">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <strong style="color:var(--text-main);">🔹 {phase['phase'].title()} Phase</strong>
                        <span style="color:{p_color};border:1px solid {p_color};padding:2px 12px;
                                     border-radius:20px;font-size:0.78rem;">
                            {phase['priority'].title()} Priority
                        </span>
                    </div>
                    <p style="margin:0.6rem 0 0.2rem; color:var(--text-main);"><strong>Focus:</strong> {phase['focus'].title()}</p>
                    <p style="margin:0.2rem 0; color:var(--text-main);"><strong>Goal:</strong> {phase['goal']}</p>
                    <p style="margin:0.2rem 0;color:var(--text-muted);font-size:0.87rem;">⏱ Est. time: {phase['estimated_time']}</p>
                </div>""", unsafe_allow_html=True)

        if report.get('resources'):
            st.subheader("📖 Recommended Resources")
            for r in report['resources']:
                st.markdown(f"""
                    <div style="background:var(--card-bg);padding:0.9rem;border-radius:10px;margin:0.4rem 0; border:1px solid var(--card-border);">
                        <a href="{r['url']}" target="_blank"
                           style="text-decoration:none;color:var(--primary-color);font-weight:500;">
                            📘 {r['name']}
                        </a>
                        <span style="float:right;color:var(--text-muted);font-size:0.82rem;">{r['type'].title()}</span>
                    </div>""", unsafe_allow_html=True)

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
            use_container_width=True,
            type="primary"
        )
