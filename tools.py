import logging
from typing import Dict, Any

# Setup logger for tools
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ESGenieTools")

def calculate_carbon_footprint(electricity_kwh: float, fuel_litres: float) -> float:
    """Calculates Scope 1 & 2 carbon footprint based on GHG Protocol."""
    # Scope 2: Malaysia Grid Emission Factor (0.585 kgCO2e/kWh -> 0.000585 tCO2e/kWh)
    scope2_emission = electricity_kwh * 0.000585  
    # Scope 1: Standard Petrol/Diesel conversion (approx 0.00232 tCO2e/litre)
    scope1_emission = fuel_litres * 0.00232           
    total = scope1_emission + scope2_emission
    logger.info(f"Tool executed: calculate_carbon -> Scope 1 & 2 Total: {total:.4f} tCO2e")
    return round(total, 4)

def check_bursa_compliance(industry: str, pdpa_status: str, macc_status: str) -> Dict[str, Any]:
    """Checks compliance against Bursa MMLR, PDPA 2010, and MACC Act s.17A."""
    compliance_score = 100
    flags = []
    if pdpa_status.lower() != "pdpa compliant":
        compliance_score -= 15
        flags.append("PDPA 2010 Violation Risk")
    if macc_status.lower() == "no policy":
        compliance_score -= 20
        flags.append("MACC Act s.17A Corporate Liability Risk")
    
    logger.info(f"Tool executed: check_bursa_compliance -> Score: {compliance_score}")
    return {"status": f"{compliance_score}% Compliant", "flags": flags}

def compute_esg_scores(data: Dict) -> Dict:
    """Programmatically calculates weighted E/S/G scores (40/35/25 weights)."""
    # E-Score: Base 50 + waste diversion bonus
    waste = max(data.get('waste_kg', 1), 1)
    diversion_rate = (data.get('waste_recycled_kg', 0) / waste) * 100
    e_score = min(100, 50 + (diversion_rate * 0.5))
    
    # S-Score: Based on diversity, training, and local supply
    s_score = min(100, (data.get('women_in_leadership_pct', 0) * 1.5) + (data.get('avg_training_hours', 0) * 2) + (data.get('local_supplier_pct', 0) * 0.5))
    
    # G-Score: Based on policy existence
    g_score = 100
    if data.get('pdpa_status') != "PDPA Compliant": g_score -= 30
    if data.get('macc_status') == "No Policy": g_score -= 40
    if data.get('esg_policy') == "No Commitment": g_score -= 20
    
    total = (e_score * 0.40) + (s_score * 0.35) + (max(g_score, 0) * 0.25)
    return {"E": round(e_score, 1), "S": round(s_score, 1), "G": max(round(g_score, 1), 0), "Total": round(total, 1)}