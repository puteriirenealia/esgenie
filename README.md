# 🌿 ESGnie Agents: SME Readiness Report Orchestrator

**Built for the #GeminiNexus Hackathon 2026**

ESGnie is a localized, Human-in-the-Loop (HITL) multi-agent orchestrator designed to help Malaysian SMEs assess their Environmental, Social, and Governance (ESG) maturity against national standards.

## 🏆 Alignment with Judging Criteria

* **Agentic Agency & Recovery (40%):** A sequential pipeline of specialized agents (Carbon, Compliance, Risk, Report) passes contextual states. Includes `_execute_agent_with_recovery` for exponential backoff during API failures.
* **Technical Depth (30%):** Utilizes Google GenAI SDK with structured Pydantic schemas for Gemini Vision. Agents execute strict pure-Python tools mapped to Malaysian frameworks (MACC Act s.17A, PDPA 2010, Bursa MMLR, and 0.585 kgCO2e/kWh Grid EFs).
* **System Robustness (20%):** Features a strict HITL workflow to prevent AI hallucination of financial/environmental metrics. Implements `SafetySetting` configurations to block dangerous content.
* **Docs & Demo (10%):** Features a live Streamlit UI with a real-time "Agent Console" to expose the orchestrator's reasoning traces, crowned by an autonomous LLM-as-a-Judge evaluation.

## 🧩 Multi-Agent Architecture

```mermaid
graph TD
    A[User Uploads Utility Bills] --> B(BillScannerAgent: Gemini Vision)
    B --> C{Human-in-the-Loop Validation}
    C -->|Approves Data| D(CarbonAgent: Scope 1 & 2 Tools)
    D --> E(ComplianceAgent: MACC/PDPA/Bursa)
    E --> F(BenchmarkAgent: FY2024 Peer Data)
    F --> G(RiskFlagAgent: Prioritization)
    G --> H(ReportAgent: E/S/G Scoring & Narrative)
    H --> I[Final Board Report & Visual Dashboard]
    I --> J{LLM Judge: Quality Assurance}

🚀 Live Demo: [https://esgenie-218585510823.asia-southeast1.run.app/]

🚨 The ESG Mandate: Why Malaysian SMEs Must Act Now
The Catalyst: Bursa Malaysia has mandated strict ESG and climate reporting for Public Listed Companies (PLCs).

The Trickle-Down Effect: PLCs are now required to report Scope 3 emissions and audit their entire supply chain. If an SME cannot provide verified ESG data, listed companies will drop them as vendors to remain compliant.

The Reality for SMEs:

Lost Contracts: ESG readiness is now a strict gatekeeper for B2B tenders and corporate procurement.

Denied Financing: Local banks increasingly tie loan approvals and lower interest rates to ESG performance.

The Barrier: SMEs lack the budget for expensive consultants to navigate complex frameworks like GHG Scope 1 & 2, MACC s.17A, and PDPA.

The Solution:
ESGnie Agents eliminates the cost and complexity. By simply uploading utility bills, our multi-agent AI autonomously calculates emissions, audits legal compliance, and generates a board-ready, Bursa-benchmarked ESG report in seconds.
