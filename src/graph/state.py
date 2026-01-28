# src/graph/state.py
from typing import TypedDict, List, Dict, Optional

class GraphState(TypedDict):
    # 이 줄이 반드시 있어야 함!
    image_data: bytes 
    redness: float
    oiliness: float
    user_allergy: List[str]
    analysis_result: Dict
    skin_knowledge: str
    recommended_products: List[Dict]
    final_report: str