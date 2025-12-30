import streamlit as st
import pandas as pd

def render_score_card(role_result):
    """
    Renders the Elite Score Dashboard with decomposition.
    """
    final_score = role_result.get("score", 0)
    skill_score = role_result.get("skill_score", 0)
    lang_score = role_result.get("language_score", 0)
    penalties = role_result.get("penalties", [])
    breakdown = role_result.get("breakdown", {})
    
    # 1. Main Score Header
    st.markdown(f"""
        <div style="background: rgba(0, 209, 255, 0.1); border: 1px solid #00D1FF; border-radius: 10px; padding: 20px; text-align: center; margin-bottom: 20px;">
            <h3 style="margin:0; color: #00D1FF;">ROLE FIT: {final_score}%</h3>
            <div style="font-size: 0.8rem; color: #aaa; margin-top: 5px;">
                Weighted Algorithmic Match against 2025 Industry Baseline
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Decomposition Columns
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("SKILL MATCH (70%)", f"{skill_score}%", help="Based on weighted overlap with Core/Secondary/Optional skills")
        st.progress(min(100, int(skill_score)))
        
    with c2:
        st.metric("CONFIDENCE (30%)", f"{lang_score}%", help="Based on linguistic action-verbs vs hedging analysis")
        st.progress(min(100, int(lang_score)))
        
    with c3:
        n_pen = len(penalties)
        st.metric("PENALTIES APPLIED", f"{n_pen}", delta=f"-{n_pen * 15}% Impact" if n_pen > 0 else "None", delta_color="inverse")
    
    # 3. Penalty Explanation
    if penalties:
        st.error(f"⚠️ **PENALTY ACTIVE:** {penalties[0]}")
        st.caption("Penalties are applied for missing 'Core Skills' which are non-negotiable for this role.")

    # 4. Detailed Breakdown
    with st.expander("📊 View Mathematical Decomposition"):
        st.json(breakdown)

def render_evidence_table(signals, role_result):
    """
    Renders the evidence table showing why skills were matched.
    """
    st.markdown("### 🔍 Verified Skill Evidence")
    
    # Flatten evidence
    evidence_rows = []
    
    # From signals (NLP extracted)
    extracted_skills = {s.get("skill", s.get("name")): s for s in signals.get("skills", [])}
    
    matched_skills = role_result.get("matched", [])
    
    for skill in matched_skills:
        # Find in extracted
        meta = extracted_skills.get(skill)
        if meta:
            evidence_list = meta.get("evidence", [])
            confidence = meta.get("confidence", 1.0)
            
            # If no specific sentence evidence (e.g. from structured input), explicit note
            snippet = evidence_list[0] if evidence_list else "Derived from Structured Intake"
            
            evidence_rows.append({
                "Skill": skill,
                "Confidence": f"{confidence:.2f}",
                "Source Evidence": snippet
            })
        else:
            # Fallback for structured input matches
            evidence_rows.append({
                "Skill": skill,
                "Confidence": "1.00",
                "Source Evidence": "Explicitly claimed in System Intake"
            })
            
    if evidence_rows:
        df = pd.DataFrame(evidence_rows)
        st.dataframe(
            df, 
            column_config={
                "Skill": st.column_config.TextColumn("Verified Skill", width="medium"),
                "Confidence": st.column_config.ProgressColumn("NLP Confidence", format="%.2f", min_value=0, max_value=1),
                "Source Evidence": st.column_config.TextColumn("Linguistic Proof", width="large"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No skill evidence found. Run analysis to populate.")

def render_confidence_trace(signals):
    """
    Visualizes the linguistic confidence trace.
    """
    st.markdown("### 🗣️ Linguistic Confidence X-Ray")
    
    score = signals.get("confidence_score", 0)
    trace = signals.get("confidence_trace", [])
    
    st.markdown(f"""
    **Confidence Score: {int(score * 100)}/100**  
    *Formula: (Action_Verbs × 1.5 - Hedge_Words) / Total_Sentences*
    """)
    
    st.info("💡 **Analysis:** We scan every sentence for 'Assertive Action Verbs' vs 'Weak Hedging Language'.")
    
    if not trace:
        st.warning("No linguistic trace available.")
        return

    # Filter to interesting sentences to save space
    for item in trace:
        sent = item["sentence"]
        classification = item["classification"]
        
        if classification == "assertive":
            st.markdown(f"✅ **+1.5 (Assertive):** ...{sent}...", help=f"Action Verbs: {item['action_verbs']}")
        elif classification == "hedged":
            st.markdown(f"⚠️ **-1.0 (Hedged):** ...{sent}...", help=f"Hedge Markers: {item['hedge_markers']}")
