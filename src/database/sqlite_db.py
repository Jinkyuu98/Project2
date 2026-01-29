import sqlite3
import os

# DB 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "db", "skin_products.db")

def get_recommended_products(oiliness, redness, allergy_ingredients=None):
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    skin_type = "지성" if oiliness > 70 else "건성" if oiliness < 40 else "복합성"
    is_sensitive = redness > 40
    
    # 💡 [수정 1] 루틴 순서 및 카테고리/최소가격 정의
    # 'search' 대신 DB의 'category' 컬럼과 100% 일치하는 값을 사용해
    routine_config = [
        {"step": "스킨/토너", "db_cat": "스킨/토너", "min_price": 8000},
        {"step": "에센스/세럼/앰플", "db_cat": "에센스/세럼/앰플", "min_price": 10000},
        {"step": "로션", "db_cat": "로션", "min_price": 8000},
        {"step": "크림", "db_cat": "크림", "min_price": 10000}
    ]
    
    products = []
    
    # 알레르기 성분 처리
    allergy_filter = ""
    params_base = []
    if allergy_ingredients:
        for ing in allergy_ingredients:
            # 💡 [보안] 공백 없이 매칭되도록 더 꼼꼼하게 처리
            allergy_filter += " AND ingredients NOT LIKE ?"
            params_base.append(f"%{ing.strip()}%")

    for item in routine_config:
        # 💡 [수정 2] 핵심 쿼리: 정확한 카테고리(=) + 최소 가격 하한선(>=)
        query = f"""
            SELECT * FROM products 
            WHERE category = ? 
            AND price >= ?
            {allergy_filter}
            AND (product_spec LIKE ? OR ingredients LIKE '%진정%' OR ingredients LIKE '%병풀%')
            ORDER BY 
                (CASE WHEN ? = 1 AND (ingredients LIKE '%진정%' OR ingredients LIKE '%병풀%') THEN 0 ELSE 1 END) ASC,
                (CASE WHEN product_spec LIKE ? THEN 0 ELSE 1 END) ASC,
                price ASC -- 💡 이미 int형이므로 바로 정렬
            LIMIT 1
        """
        
        # 💡 파라미터 순서: 카테고리, 최소가격, 알레르기성분들, 피부타입, 민감여부, 피부타입
        current_params = [item['db_cat'], item['min_price']] + params_base + [f"%{skin_type}%", 1 if is_sensitive else 0, f"%{skin_type}%"]
        
        cursor.execute(query, current_params)
        row = cursor.fetchone()
        
        if row:
            p = dict(row)
            p['display_category'] = item['step']
            # detail_url이나 link 중 있는 것을 사용
            p['detail_url'] = p.get('detail_url', p.get('link', ''))
            products.append(p)

    conn.close()
    return products