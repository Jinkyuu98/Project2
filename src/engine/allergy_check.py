# 1. 식약처 지정 알레르기 유발 성분 25종 리스트 (그대로 유지)
SYSTEM_ALLERGY_LIST = [
    "아밀신남알", "벤질알코올", "신나밀알코올", "시트랄", "유제놀", 
    "하이드록시시트로넬알", "아이소유제놀", "아밀신나밀알코올", "벤질살리실레이트", 
    "신남알", "쿠마린", "제라니올", "아니스알코올", "벤질신나메이트", 
    "파네솔", "부틸페닐메틸프로피오날", "리날룰", "벤질벤조에이트", 
    "시트로넬올", "헥실신남알", "리모넨", "메틸 2-옥티노에이트", 
    "알파-아이소메틸아이오논", "참나무이끼추출물", "나무이끼추출물"
]

def check_product_safety(ingredients_str, is_wash_off):
    """
    제품 성분을 분석하여 사용자에게 정중한 존댓말로 안내 메시지를 반환합니다.
    """
    product_ingredients = [i.strip() for i in ingredients_str.split(',')]
    found_allergens = [a for a in SYSTEM_ALLERGY_LIST if a in product_ingredients]
    
    # 1. 검출된 성분이 없는 경우
    if not found_allergens:
        return "✅ 해당 제품은 식약처 고시 알레르기 유발 성분이 포함되어 있지 않아 안심하고 사용하셔도 좋습니다."

    # 2. 검출된 성분이 있는 경우
    if is_wash_off == 0:
        threshold = "0.001%"
        p_type = "흡수시키는"
    else:
        threshold = "0.01%"
        p_type = "씻어내는"

    detected_names = ", ".join(found_allergens)
    
    # 정중한 존댓말로 구성된 최종 메시지
    message = (
        f"⚠️ 주의: 해당 제품에서 알레르기 유발 주의 성분인 [{detected_names}]이(가) 포함된 것으로 확인되었습니다. "
        f"이 제품은 {p_type} 타입으로, 식약처 기준상 {threshold}를 초과할 경우 의무적으로 표시하도록 되어 있습니다. "
        f"민감한 피부를 가지셨다면 사용 전 귀 뒤쪽 등에 패치 테스트를 먼저 해보시길 권장드립니다."
    )
    
    return message