import streamlit as st
from agents import ESGenieOrchestrator
from tools import compute_esg_scores
import time

# ==========================================
# UI SETUP & STYLING
# ==========================================
st.set_page_config(page_title="ESGnie Agents", page_icon="🌿", layout="wide")

st.markdown("""
<style>
    .reportview-container { background-color: #0E1117; }
    h1, h2, h3 { color: #4ade80 !important; font-family: 'Courier New', monospace; }
    .stButton>button { background-color: #166534; color: white; border: 1px solid #4ade80; width: 100%; font-family: monospace; }
    .stButton>button:hover { background-color: #15803d; border-color: white; }
    .console-box { background-color: #000000; border: 1px solid #333; border-radius: 5px; padding: 15px; font-family: monospace; color: #4ade80; font-size: 0.85em; height: 600px; overflow-y: auto;}
    .section-divider { border-bottom: 1px solid #333; margin: 20px 0; color: #666; font-size: 0.8em; font-weight: bold; text-transform: uppercase; letter-spacing: 2px;}
</style>
""", unsafe_allow_html=True)

if 'scanned' not in st.session_state:
    st.session_state.scanned = False
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = {}
if 'pipeline_complete' not in st.session_state:
    st.session_state.pipeline_complete = False

st.markdown("<h1 style='text-align: center; font-size: 3em;'>ESGnie Agents</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888; font-family: monospace;'>ESG Readiness Report for SME for #GeminiNexus Hackathon 2026</p>", unsafe_allow_html=True)
st.write("---")

col_left, col_right = st.columns([2, 1], gap="large")

orchestrator = ESGenieOrchestrator()

# ==========================================
# RIGHT COLUMN: AGENT CONSOLE
# ==========================================
with col_right:
    st.markdown("### 🟢 AGENT CONSOLE")
    console_placeholder = st.empty()
    
    def update_console(logs: list):
        log_html = "<div class='console-box'>"
        for log in logs:
            log_html += f"<p>> {log}</p>"
        log_html += "</div>"
        console_placeholder.markdown(log_html, unsafe_allow_html=True)

    if 'logs' not in st.session_state:
        st.session_state.logs = ["SYSTEM INITIALIZED. IDLE."]
    
    update_console(st.session_state.logs)

# ==========================================
# LEFT COLUMN: HITL WORKFLOW
# ==========================================
with col_left:
    st.markdown("### 🔍 Bill Scanner (Gemini Vision)")
    uploaded_files = st.file_uploader("Drag & drop bill photos here (TNB, PETRONAS, AIR SELANGOR)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if st.button("Extract Data from Bills"):
        st.session_state.logs.append("AGENT PLAN: Extracting metrics from images...")
        update_console(st.session_state.logs)
        
        with st.spinner("Vision Agent analyzing documents..."):
            extracted = orchestrator.bill_scanner_agent(image_paths=uploaded_files)
            st.session_state.extracted_data = extracted
            st.session_state.scanned = True
            
            st.session_state.logs.append("EXTRACTION RESULT: Success. Awaiting human validation.")
            update_console(st.session_state.logs)

    if st.session_state.scanned:
        st.markdown("<div class='section-divider'>⚙️ Company ESG Data (Review & Edit)</div>", unsafe_allow_html=True)
        
        d = st.session_state.extracted_data
        
        c1, c2 = st.columns(2)
        company_name = c1.text_input("COMPANY NAME", value=d.get("company_name", ""))
        industry_sector = c2.selectbox("INDUSTRY SECTOR", ["Manufacturing", "Technology & IT", "Services", "Agriculture"], index=0)
        
        st.markdown("<div class='section-divider'>ENVIRONMENTAL METRICS</div>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        electricity_kwh = c3.number_input("MONTHLY ELECTRICITY (KWH) - TNB", value=float(d.get("electricity_kwh", 0)))
        fuel_litres = c4.number_input("MONTHLY FUEL (LITRES) - PETRONAS", value=float(d.get("fuel_litres", 0)))
        c5, c6 = st.columns(2)
        waste_kg = c5.number_input("MONTHLY WASTE (KG) - ALAM FLORA", value=float(d.get("waste_kg", 0)))
        waste_recycled_kg = c6.number_input("WASTE RECYCLED (KG)", value=float(d.get("waste_recycled_kg", 0)))
        water_m3 = st.number_input("WATER CONSUMPTIONS (M³) - AIR SELANGOR", value=float(d.get("water_m3", 0)))

        st.markdown("<div class='section-divider'>SOCIAL METRICS</div>", unsafe_allow_html=True)
        c7, c8 = st.columns(2)
        total_employees = c7.number_input("TOTAL EMPLOYEES", value=int(d.get("total_employees", 0)))
        women_in_leadership_pct = c8.number_input("% WOMEN IN LEADERSHIP", value=float(d.get("women_in_leadership_pct", 0)))
        c9, c10 = st.columns(2)
        avg_training_hours = c9.number_input("AVERAGE TRAINING HOURS", value=float(d.get("avg_training_hours", 0)))
        local_supplier_pct = c10.number_input("% BUDGET SPENT ON LOCAL SUPPLIERS", value=float(d.get("local_supplier_pct", 0)))

        st.markdown("<div class='section-divider'>GOVERNANCE METRICS</div>", unsafe_allow_html=True)
        c11, c12, c13 = st.columns(3)
        macc_status = c11.selectbox("ANTI-BRIBERY (MACC)", ["No Policy", "In Progress", "MACC Compliant"], index=0 if d.get("macc_status") == "No Policy" else 2)
        pdpa_status = c12.selectbox("DATA PRIVACY (PDPA)", ["Non-Compliant", "PDPA Compliant"], index=1 if d.get("pdpa_status") == "PDPA Compliant" else 0)
        esg_policy = c13.selectbox("ESG POLICY", ["No Commitment", "Drafting", "Published"], index=0)

        st.write("")
        if st.button("🧠 Launch ESG Agent ->", type="primary"):
            human_reviewed_data = {
                "company_name": company_name,
                "industry_sector": industry_sector,
                "electricity_kwh": electricity_kwh,
                "fuel_litres": fuel_litres,
                "waste_kg": waste_kg,
                "waste_recycled_kg": waste_recycled_kg,
                "water_m3": water_m3,
                "total_employees": total_employees,
                "women_in_leadership_pct": women_in_leadership_pct,
                "avg_training_hours": avg_training_hours,
                "local_supplier_pct": local_supplier_pct,
                "macc_status": macc_status,
                "pdpa_status": pdpa_status,
                "esg_policy": esg_policy
            }

            st.session_state.logs.append("Human validation complete. Launching multi-agent pipeline...")
            update_console(st.session_state.logs)
            
            with st.spinner("Agents are analyzing your data..."):
                try:
                    st.session_state.logs.append(f"Executing CarbonAgent(electricity={electricity_kwh}, fuel={fuel_litres})...")
                    update_console(st.session_state.logs)
                    human_reviewed_data = orchestrator.carbon_agent(human_reviewed_data)
                    
                    st.session_state.logs.append("Executing ComplianceAgent(Bursa MMLR, MACC s.17A, PDPA 2010)...")
                    update_console(st.session_state.logs)
                    human_reviewed_data = orchestrator.compliance_agent(human_reviewed_data)
                    
                    st.session_state.logs.append("Executing BenchmarkAgent(Bursa FY2024)...")
                    update_console(st.session_state.logs)
                    human_reviewed_data = orchestrator.benchmark_agent(human_reviewed_data)
                    
                    st.session_state.logs.append("Executing RiskFlagAgent(Legal exposure & categorization)...")
                    update_console(st.session_state.logs)
                    human_reviewed_data = orchestrator.risk_flag_agent(human_reviewed_data)
                    
                    st.session_state.logs.append("Executing ReportAgent(Drafting executive narrative & scoring E/S/G)...")
                    update_console(st.session_state.logs)
                    final_report = orchestrator.report_agent(human_reviewed_data)
                    
                    st.session_state.logs.append("Executing LLMJudge(Quality Assurance)...")
                    update_console(st.session_state.logs)
                    evaluation = orchestrator.llm_judge_evaluation(final_report)
                    
                    st.session_state.logs.append("PIPELINE COMPLETE.")
                    update_console(st.session_state.logs)
                    
                    st.session_state.final_report = final_report
                    st.session_state.evaluation = evaluation
                    st.session_state.final_data = human_reviewed_data
                    st.session_state.pipeline_complete = True
                    
                except Exception as e:
                    st.error(f"Pipeline Failed: {e}")
                    st.session_state.logs.append(f"ERROR: {e}")
                    update_console(st.session_state.logs)

# ==========================================
# BOTTOM SECTION: FINAL REPORT
# ==========================================
if st.session_state.pipeline_complete:
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>📄 Agent Intelligence Report</h2>", unsafe_allow_html=True)
    
    # --- VISUAL ESG SCORECARD ---
    scores = compute_esg_scores(st.session_state.final_data)
    
    st.markdown("### 📊 ESG Readiness Scorecard")
    sc1, sc2, sc3, sc4 = st.columns(4)
    
    sc1.metric("🏆 Overall Score", f"{scores['Total']}%")
    sc2.metric("🌍 Environment (40%)", f"{scores['E']}%")
    sc3.metric("👥 Social (35%)", f"{scores['S']}%")
    sc4.metric("⚖️ Governance (25%)", f"{scores['G']}%")
    
    # Visual Progress Bar
    st.progress(int(scores['Total']), text="Overall ESG Maturity Readiness")
    st.write("---")
    # -----------------------------
    
    r_col1, r_col2 = st.columns([2, 1])
    with r_col1:
        st.info("This report was autonomously generated by the ESGenie ReportAgent.")
        st.markdown(st.session_state.final_report)
    with r_col2:
        st.warning("⚖️ LLM Judge Quality Assessment")
        st.markdown(st.session_state.evaluation)