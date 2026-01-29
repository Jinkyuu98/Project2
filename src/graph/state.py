# src/graph/state.py
from typing import TypedDict, List, Dict, Optional

class GraphState(TypedDict):
    # 이 줄이 반드시 있어야 함!
    image_data: bytes 
    user_message: str      # 💡 [추가] 유저 입력 메시지
    user_concerns: str     # 💡 [추가] 유저 고민/관심사 (intent_node에서 추출)
    redness: float
    oiliness: float
    user_allergy: List[str]
    analysis_result: Dict
    skin_knowledge: str
    recommended_products: List[Dict]
    final_report: str