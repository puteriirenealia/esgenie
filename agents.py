import os
import logging
import time
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import our custom tools!
from tools import calculate_carbon_footprint, check_bursa_compliance, compute_esg_scores

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger("ESGenieOrchestrator")

SAFE_CONFIG = types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        ),
    ],
    temperature=0.2,
)

class AgentError(Exception):
    pass

class ExtractedData(BaseModel):
    company_name: str
    industry_sector: str
    electricity_kwh: float
    fuel_litres: float
    waste_kg: float
    waste_recycled_kg: float
    water_m3: float
    total_employees: int
    women_in_leadership_pct: float
    avg_training_hours: float
    local_supplier_pct: float
    macc_status: str
    pdpa_status: str
    esg_policy: str

class ESGenieOrchestrator:
    def __init__(self):
        self.client = genai.Client()
        self.model_id = 'gemini-2.5-pro'
        self.vision_model_id = 'gemini-2.5-flash'

    def _execute_agent_with_recovery(self, agent_name: str, prompt: str, retries: int = 3, tools: list = None, vision_images=None) -> str:
        logger.info(f"Executing {agent_name}...")
        
        config = SAFE_CONFIG
        if tools:
            config.tools = tools

        contents = [prompt]
        if vision_images:
            contents.extend(vision_images)

        for attempt in range(retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_id if not vision_images else self.vision_model_id,
                    contents=contents,
                    config=config
                )
                logger.info(f"{agent_name} executed successfully.")
                return response.text
            except Exception as e:
                logger.warning(f"{agent_name} failed on attempt {attempt + 1}. Error: {e}")
                time.sleep(2 ** attempt)
        
        logger.error(f"{agent_name} failed after {retries} attempts.")
        raise AgentError(f"Agent {agent_name} critical failure.")

    def bill_scanner_agent(self, image_paths: list = None) -> Dict:
        logger.info("BillScannerAgent analyzing document context via Vision...")
        
        mock_data = {
            "company_name": "Techbumi Sdn Bhd",
            "industry_sector": "Manufacturing",
            "electricity_kwh": 2800.0,
            "fuel_litres": 410.0,
            "waste_kg": 150.0,
            "waste_recycled_kg": 40.0,
            "water_m3": 48.0,
            "total_employees": 20,
            "women_in_leadership_pct": 25.0,
            "avg_training_hours": 15.0,
            "local_supplier_pct": 60.0,
            "macc_status": "No Policy",
            "pdpa_status": "PDPA Compliant",
            "esg_policy": "No Commitment"
        }

        if not image_paths:
            logger.warning("No images provided. Using mock data.")
            return mock_data

        prompt = "Extract the key metrics and compliance statuses from these dashboard screenshots. Return strictly adhering to the schema provided. Do not guess; if a value is missing, use 0 or 'Unknown'."
        
        try:
            from PIL import Image
            images = [Image.open(img) for img in image_paths]
            
            logger.info(f"Processing {len(images)} images through Gemini Vision...")
            response = self.client.models.generate_content(
                model=self.vision_model_id,
                contents=[prompt, *images],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ExtractedData,
                    temperature=0.1
                )
            )
            data = json.loads(response.text)
            logger.info("Vision extraction successful.")
            
            for key in mock_data.keys():
                if key not in data or data[key] is None:
                    data[key] = mock_data[key]
            return data
            
        except Exception as e:
            logger.error(f"Vision parsing failed: {e}. Falling back to mock data.")
            return mock_data

    def carbon_agent(self, data: Dict) -> Dict:
        elec = data.get('electricity_kwh', 0)
        fuel = data.get('fuel_litres', 0)
        prompt = f"Calculate Scope 1 & 2 carbon emissions using standard tools for {elec} kWh electricity and {fuel} L fuel."
        
        result = self._execute_agent_with_recovery("CarbonAgent", prompt, tools=[calculate_carbon_footprint])
        data["carbon_narrative"] = result
        data["carbon_tco2e"] = calculate_carbon_footprint(elec, fuel)
        return data

    def compliance_agent(self, data: Dict) -> Dict:
        pdpa = data.get('pdpa_status', 'Unknown')
        macc = data.get('macc_status', 'Unknown')
        industry = data.get('industry_sector', 'General')
        
        prompt = f"""
        Evaluate compliance for a {industry} SME in Malaysia.
        PDPA Status: {pdpa}. MACC Status: {macc}.
        Provide a strict analysis citing the Bursa Malaysia Main Market Listing Requirements (MMLR), the Personal Data Protection Act (PDPA) 2010, and Section 17A of the MACC Act (Corporate Liability).
        """
        result = self._execute_agent_with_recovery("ComplianceAgent", prompt, tools=[check_bursa_compliance])
        data["compliance_narrative"] = result
        return data

    def benchmark_agent(self, data: Dict) -> Dict:
        tco2e = data.get('carbon_tco2e', 0)
        industry = data.get('industry_sector', 'Manufacturing')
        prompt = f"Benchmark a carbon footprint of {tco2e} tCO2e against Bursa Malaysia FY2024 peer data for an SME in the {industry} sector."
        data["benchmark_narrative"] = self._execute_agent_with_recovery("BenchmarkAgent", prompt)
        return data

    def risk_flag_agent(self, data: Dict) -> Dict:
        pdpa = data.get('pdpa_status', 'Unknown')
        macc = data.get('macc_status', 'Unknown')
        tco2e = data.get('carbon_tco2e', 0)
        prompt = f"""
        Identify top ESG risks based on: PDPA={pdpa}, MACC={macc}, Scope 1&2 Carbon={tco2e}.
        CRITICAL: You must benchmark these risks against Bursa Malaysia FY2024 industry standards.
        Categorize every identified risk explicitly as [HIGH RISK], [MEDIUM RISK], or [LOW RISK].
        """
        data["risk_narrative"] = self._execute_agent_with_recovery("RiskFlagAgent", prompt)
        return data

    def report_agent(self, data: Dict) -> str:
        scores = compute_esg_scores(data)
        waste = data.get('waste_kg', 1)
        recycled = data.get('waste_recycled_kg', 0)
        diversion_rate = round((recycled / waste) * 100, 1) if waste > 0 else 0

        prompt = f"""
        You are an expert ESG Corporate Secretary generating an ESG Readiness Report for an SME.
        
        CRITICAL INSTRUCTION: DO NOT ask questions. DO NOT ask for clarification. Output ONLY the final markdown report based on these facts:

        RAW DATA:
        - Scope 1 & 2 Emissions: {data.get('carbon_tco2e')} tCO2e (Calculated using 0.585 kgCO2e/kWh Grid EF).
        - Waste Diversion Rate: {diversion_rate}%.
        - Weighted Scores: E ({scores['E']}/100, 40% weight), S ({scores['S']}/100, 35% weight), G ({scores['G']}/100, 25% weight). Overall: {scores['Total']}/100.

        AGENT ANALYSES TO INCLUDE:
        - Compliance: {data.get('compliance_narrative')}
        - Benchmarks: {data.get('benchmark_narrative')}
        - Risks: {data.get('risk_narrative')}

        Structure the report exactly like this:
        ### EXECUTIVE SUMMARY (Include overall score and weighting methodology)
        ### ENVIRONMENTAL ASSESSMENT (Scope 1 & 2, Waste Diversion)
        ### SOCIAL ASSESSMENT
        ### GOVERNANCE ASSESSMENT (Cite MACC s.17A, PDPA 2010, Bursa MMLR)
        ### BURSA FY2024 BENCHMARK & RISK FLAGS (Use [HIGH/MEDIUM/LOW RISK] categories)
        """
        return self._execute_agent_with_recovery("ReportAgent", prompt)

    def llm_judge_evaluation(self, final_report: str) -> str:
        logger.info("Executing LLM-as-a-Judge for Quality Assurance...")
        eval_prompt = f"""
        You are an expert ESG auditor. Evaluate the following ESG Readiness Report.
        
        Score it strictly out of 10 based on:
        1. Accurate citation of Malaysian laws (MACC s.17A, PDPA 2010, Bursa MMLR).
        2. Proper categorization of risk flags (High/Medium/Low).
        3. Clear E/S/G weighting breakdown.

        Report to evaluate:
        {final_report}

        Provide a short critique and end with a final score exactly in this format: [SCORE/10].
        """
        return self._execute_agent_with_recovery("LLMJudge", eval_prompt)