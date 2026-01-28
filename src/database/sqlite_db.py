import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "db", "skin_products.db")

def get_recommended_products(oiliness, redness, limit=3):
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. 키워드 준비 (지수님 가이드 40/70 기준에 맞춰 수정)
    # 유분이 40 미만이면 건성, 70 이상이면 지성, 그 사이는 복합성(둘 다 검색 허용)
    if oiliness > 70:
        skin_type = "지성"
    elif oiliness < 40:
        skin_type = "건성"
    else:
        skin_type = "복합성" # 또는 "%" (와일드카드)를 써서 전체 검색 허용 가능

    # 홍조 수치 기준도 40으로 하향 조정
    is_sensitive = redness > 40 
    
    # 2. 쿼리 최적화
    # 민감성(is_sensitive)일 경우 '진정' 키워드를 강제로 포함하도록 OR 조건을 강화합니다.
    condition_sql = ""
    if is_sensitive:
        condition_sql = "OR ingredients LIKE '%진정%' OR ingredients LIKE '%병풀%'"

    query = f"""
        SELECT * FROM products 
        WHERE (product_spec LIKE ? {condition_sql})
        ORDER BY 
            (CASE WHEN product_spec LIKE ? THEN 0 ELSE 1 END), 
            (CASE WHEN ingredients LIKE '%진정%' THEN 0 ELSE 1 END),
            RANDOM() 
        LIMIT ?
    """
    
    cursor.execute(query, (f"%{skin_type}%", f"%{skin_type}%", limit))
    rows = cursor.fetchall()
    
    # ... (이후 변환 로직 동일)
    products = []
    for row in rows:
        p = dict(row)
        p['detail_url'] = p.get('detail_url', p.get('link', ''))
        p['is_wash_off'] = "클렌징" in p.get('category', '')
        products.append(p)

    conn.close()
    return products