import streamlit as st
import time
from pathlib import Path

# Config & Utils
from config import settings
from utils.logging_config import logger
from utils.loaders import extract_resume_text
from utils.models import UserProfile

# NLP Core
from nlp.nlp_engine import analyze_text
from intelligence.ontology import normalize_skills
from intelligence.role_matcher import calculate_role_fit
from intelligence.gap_analysis import gap_analysis

# New Analytics & Vis
from analytics.vector_analytics import calculate_skill_vector
from visualization.radar_chart import render_radar_chart
from visualization.network_graph import render_skill_network
from visualization.heatmap import render_resume_heatmap
from ai_core.synthesis import generate_roadmap
from ai_core.explorer import suggest_exploration, generate_projects

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Career Compass",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS / THEME ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap');
    
    /* Global Reset */
    .stApp {
        background-color: #050505;
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #FFFFFF;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .glass-card:hover {
        border-color: rgba(0, 114, 255, 0.4);
        transform: translateY(-2px);
    }
    
    /* Custom Button */
    .stButton > button {
        background: linear-gradient(90deg, #0072FF 0%, #00D1FF 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: opacity 0.2s;
    }
    .stButton > button:hover {
        opacity: 0.9;
        box-shadow: 0 0 15px rgba(0, 114, 255, 0.5);
    }
    
    /* Cyber Loader */
    .cyber-loader-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px 0;
        gap: 15px;
    }
    .cyber-loader {
        width: 30px;
        height: 30px;
        border: 3px solid rgba(255, 255, 255, 0.1);
        border-top: 3px solid #00D1FF;
        border-right: 3px solid #0072FF;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        box-shadow: 0 0 10px rgba(0, 209, 255, 0.5);
    }
    .cyber-loader-text {
        font-family: 'Courier New', monospace;
        color: #00D1FF;
        font-size: 14px;
        animation: pulse 1.5s infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    </style>
""", unsafe_allow_html=True)

def render_cyber_loader(text="Initializing Neural Core..."):
    return st.markdown(f"""
        <div class="cyber-loader-container">
            <div class="cyber-loader"></div>
            <div class="cyber-loader-text">{text}</div>
        </div>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if "user_profile" not in st.session_state:
    st.session_state.user_profile = None
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "exploration_data" not in st.session_state:
    st.session_state.exploration_data = None
if "project_data" not in st.session_state:
    st.session_state.project_data = None

# --- SIDEBAR: FLOW CONTROL ---
with st.sidebar:
    st.title("🧭 Career Compass")
    st.caption("v3.0.0 | Generative Strategy")
    
    mode = st.radio("Input Mode", ["📄 Resume Analysis", "🌱 Fresh Start (Manual)"])
    
    target_role = st.selectbox(
        "Target Role Model",
        ["Senior Python Developer", "Data Scientist", "Machine Learning Engineer", "DevOps Engineer", "Frontend Architect"],
        index=0
    )

    if mode == "📄 Resume Analysis":
        uploaded_file = st.file_uploader("Upload Profile Data", type=["pdf", "docx", "txt"])
        
        if st.button("Initialize Analysis", use_container_width=True, type="primary"):
            if uploaded_file:
                loader = st.empty()
                loader.markdown(f"""
                    <div class="cyber-loader-container">
                        <div class="cyber-loader"></div>
                        <div class="cyber-loader-text">READING BIO-DIGITAL SIGNALS...</div>
                    </div>
                """, unsafe_allow_html=True)
                
                try:
                    raw_text, redacted = extract_resume_text(uploaded_file)
                    
                    # NLP Engine
                    signals = analyze_text(raw_text)
                    raw_skills = [s.get('skill', s.get('name')) for s in signals['skills']]
                    normalized = normalize_skills(raw_skills)
                    skill_list = [s if isinstance(s, str) else s.get('name') for s in normalized]
                    
                    # Create Profile
                    profile = UserProfile(
                        name="Candidate",
                        raw_text=raw_text,
                        skills=skill_list,
                        target_role=target_role,
                        confidence_score=signals.get("confidence_score", 0),
                        is_manual=False
                    )
                    st.session_state.user_profile = profile
                    st.session_state.analysis_complete = True
                    
                    # Trigger GenAI
                    loader.markdown(f"""
                        <div class="cyber-loader-container">
                            <div class="cyber-loader"></div>
                            <div class="cyber-loader-text">SYNTHESIZING FUTURE PATHWAYS...</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state.exploration_data = suggest_exploration(skill_list, ["Tech"])
                    st.session_state.project_data = generate_projects(skill_list, target_role)
                    
                finally:
                    loader.empty()
            else:
                st.error("Upload a resume first.")

    else: # Fresh Start
        st.markdown("### Profile Diagnostics")
        name = st.text_input("Name", "Explorer")
        ambition = st.text_input("Career Ambition", "Become a CTO")
        
        manual_skills = st.text_area("Current Skills (Comma Separated)", "Python, Problem Solving")
        interests = st.text_area("Core Interests", "Distributed Systems, AI, Open Source")
        
        if st.button("Generate Strategy", use_container_width=True, type="primary"):
            loader = st.empty()
            with loader:
                render_cyber_loader("CONSTRUCTING NEURAL STRATEGY...")
            
            try:
                skill_list = [s.strip() for s in manual_skills.split(",") if s.strip()]
                interest_list = [s.strip() for s in interests.split(",") if s.strip()]
                
                # Normalize manually entered skills too
                normalized = normalize_skills(skill_list)
                norm_skill_list = [s if isinstance(s, str) else s.get('name') for s in normalized]

                profile = UserProfile(
                    name=name,
                    skills=norm_skill_list,
                    interests=interest_list,
                    target_role=target_role,
                    ambition=ambition,
                    is_manual=True,
                    confidence_score=8.5 # High initial confidence for manual entry
                )
                st.session_state.user_profile = profile
                st.session_state.analysis_complete = True
                
                # Trigger GenAI
                st.session_state.exploration_data = suggest_exploration(norm_skill_list, interest_list)
                st.session_state.project_data = generate_projects(norm_skill_list, ambition)
            finally:
                loader.empty()

# --- MAIN DASHBOARD ---
if st.session_state.analysis_complete and st.session_state.user_profile:
    profile = st.session_state.user_profile
    
    st.markdown(f"## Hello, {profile.name}")
    st.markdown(f"Targeting: **{profile.target_role}** | Ambition: *{profile.ambition or 'Growth'}*")
    
    # --- METRICS ROW ---
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size: 28px; font-weight: 700;">{len(profile.skills)}</div>
            <div style="color: #888; font-size: 12px;">ACTIVE SKILLS</div>
        </div>""", unsafe_allow_html=True)

    with cols[1]:
        role_fit = calculate_role_fit(profile.skills, profile.target_role, profile.confidence_score).get("score", 0)
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size: 28px; font-weight: 700; color: #00D1FF;">{role_fit}%</div>
            <div style="color: #888; font-size: 12px;">ROLE FIT</div>
        </div>""", unsafe_allow_html=True)
        
    with cols[2]:
        opps_count = len(st.session_state.exploration_data.get("opportunities", [])) if st.session_state.exploration_data else 0
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size: 28px; font-weight: 700; color: #00FF88;">{opps_count}</div>
            <div style="color: #888; font-size: 12px;">OPPORTUNITIES DETECTED</div>
        </div>""", unsafe_allow_html=True)

    # --- VISUALIZATION ROW ---
    st.markdown("### 📡 Strategic Analysis")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("**Skill Vector Radar**")
        user_vector = calculate_skill_vector(profile.skills, {})
        # Fake Baseline
        role_baseline = {"Technical": 80, "Data": 60, "Leadership": 40, "Soft Skills": 70, "Operational": 50}
        st.plotly_chart(render_radar_chart(user_vector, role_baseline), use_container_width=True)
        
    with c2:
        st.markdown("**Knowledge Graph**")
        # Hardcoded reqs for demo
        ROLE_REQUIREMENTS = {
            "Senior Python Developer": ["Python", "Django", "FastAPI", "AWS", "Docker", "PostgreSQL", "System Design", "Microservices"],
            "Data Scientist": ["Python", "Pandas", "Scikit-learn", "TensorFlow", "SQL", "Statistics", "Data Visualization"],
            "Machine Learning Engineer": ["Python", "PyTorch", "MLOps", "Kubernetes", "CUDA", "Model Serving"],
            "DevOps Engineer": ["Linux", "Terraform", "Kubernetes", "CI/CD", "AWS", "Bash", "Prometheus"],
            "Frontend Architect": ["React", "TypeScript", "Next.js", "GraphQL", "Performance Optimization", "System Design"]
        }
        reqs = ROLE_REQUIREMENTS.get(profile.target_role, ["Python"])
        missing = gap_analysis(profile.skills, reqs)
        st.plotly_chart(render_skill_network(profile.skills, missing), use_container_width=True)

    # --- TABS: DEEP DIVE ---
    st.markdown("### 🧠 Generative Compass")
    
    tabs = ["🚀 Projects & Opportunities", "🗺️ Career Roadmap"]
    if not profile.is_manual:
        tabs.insert(0, "📄 Resume Heatmap")
        
    tab_objs = st.tabs(tabs)
    
    # Resume Heatmap (Conditional)
    if not profile.is_manual:
        with tab_objs[0]:
            st.markdown(render_resume_heatmap(profile.raw_text, profile.skills), unsafe_allow_html=True)
            
    # Projects & Exploration
    idx_proj = 1 if not profile.is_manual else 0
    with tab_objs[idx_proj]:
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            st.markdown("#### 🛠️ Recommended Projects")
            if st.session_state.project_data:
                if "error" in st.session_state.project_data:
                    err_msg = st.session_state.project_data['error']
                    st.error(f"Project Logic Failed: {err_msg}")
                    if "429" in err_msg or "quota" in err_msg.lower():
                        st.warning("ℹ️ **Quota Insight**: You hit a limit despite Key Rotation. This usually means all your API Keys belong to the **same** Google Cloud Project and share one quota. Create a key in a *new* Project to fix this.")
                else:
                    for p in st.session_state.project_data.get("projects", []):
                        with st.expander(f"Build: {p['title']}", expanded=True):
                            st.markdown(f"**Tech Stack:** {', '.join(p['tech_stack'])}")
                            st.markdown(f"*{p['description']}*")
                            st.caption(f"Outcome: {p['learning_outcome']}")
            
        with col_p2:
            st.markdown("#### 🔭 Nearby Interactions")
            if st.session_state.exploration_data:
                if "error" in st.session_state.exploration_data:
                    err_msg = st.session_state.exploration_data['error']
                    st.error(f"Explorer Logic Failed: {err_msg}")
                    if "429" in err_msg or "quota" in err_msg.lower():
                        st.warning("ℹ️ **Quota Insight**: All keys likely share the same Project Quota.")
                else:
                    for i in st.session_state.exploration_data.get("nearby_interests", []):
                        st.info(f"**{i['name']}**: {i['description']}")
                    
                    st.markdown("#### ⚡ Live Opportunities")
                    for o in st.session_state.exploration_data.get("opportunities", []):
                        st.success(f"**{o['type']}**: {o['title']} ({o['action']})")

    # Roadmap
    idx_map = 2 if not profile.is_manual else 1
    with tab_objs[idx_map]:
        if st.button("Generate Detailed Month-by-Month Plan"):
             with st.spinner("Synthesizing..."):
                roadmap = generate_roadmap(profile.target_role, missing, "10h/week")
                st.json(roadmap)

else:
    # LANDING (No Analysis Yet)
    st.markdown("""
    <div style="text-align: center; padding: 100px;">
        <h1 style="font-size: 64px; background: linear-gradient(90deg, #00D1FF, #0072FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">CAREER COMPASS</h1>
        <p style="color: #888; font-size: 20px;">The Generative Engine for Professional Strategy</p>
    </div>
    """, unsafe_allow_html=True)
