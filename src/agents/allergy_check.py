# src/agents/allergy_check.py

# 식약처 기준 알레르기 유발 가능 성분 리스트 25종
SYSTEM_ALLERGY_LIST = ["아밀신남알", "벤질알코올", "신나밀알코올", "시트랄", 
                       "유제놀", "하이드록시시트로넬알","아이소유제놀","아밀신나밀알코올",
                       "벤질살리실레이트","신남알","쿠마린",
                       "제라니올","아니스알코올","벤질신나메이트",
                       "파네솔","부틸페닐메틸프로피오날","리날룰","벤질벤조에이트",
                       "시트로넬올","헥실신남알","리모넨","메틸 2-옥티노에이트",
                       "알파-아이소메틸아이오논","참나무이끼추출물","나무이끼추출물"]

def check_product_safety(ingredients, is_wash_off=False, user_allergy_list=None):
    """
    성분 문자열에서 알레르기 유발 성분(식약처 기준 + 유저 요청)을 찾고 안전 메시지 반환
    """
    # 💡 [로직 개선] 공백 무시하고 체크하기 위해 전처리
    clean_ingredients = ingredients.replace(" ", "").replace("\n", "")
    
    # 1. 식약처 기준 성분 체크
    found_system = [a for a in SYSTEM_ALLERGY_LIST if a.replace(" ", "") in clean_ingredients]
    
    # 2. 유저 맞춤 제외 요청 성분 체크 (신규)
    found_user = []
    if user_allergy_list:
        # 유저가 입력한 성분명도 공백을 제거하고 비교
        found_user = [a for a in user_allergy_list if a and a.replace(" ", "") in clean_ingredients]
    
    # 중복 제거 및 합치기 (표시용 이름은 원본 유지)
    all_found = list(set(found_system + found_user))
    
    if not all_found:
        return "✅ 이 제품은 유저 요청 및 식약처 기준 알레르기 주의 성분이 검출되지 않았습니다."
    
    msg = f"⚠️ 주의 성분({', '.join(all_found)}) 검출. "
    if found_user:
        msg += f"유저님께서 제외 요청하신 성분({', '.join(found_user)})이 포함되어 있습니다. "
    msg += f"바르는제품이므로 식약처 기준 0.01% 초과 시 표시 대상입니다."
    return msg