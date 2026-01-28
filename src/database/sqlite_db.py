import sqlite3
import os

# DB 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "db", "skin_products.db")

def get_recommended_products(oiliness, redness):
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    skin_type = "지성" if oiliness > 70 else "건성" if oiliness < 40 else "복합성"
    is_sensitive = redness > 40
    
    # 💡 1. 명확한 카테고리 순서 정의
    # (카테고리명은 DB에 저장된 실제 카테고리와 유사하게 맞추되, 중복 방지를 위해 세분화)
    routine_config = [
        {"step": "스킨/토너", "search": "토너"},
        {"step": "에센스/세럼/앰플", "search": "세럼"}, # 에센스, 앰플 포함
        {"step": "로션", "search": "로션"},
        {"step": "크림", "search": "크림"}
    ]
    
    products = []

    for item in routine_config:
        # 💡 중복 방지 로직: 이전 단계에서 뽑힌 제품은 제외 (NOT IN 사용 가능하나 여기선 ID 관리)
        exclude_ids = [p['id'] for p in products if 'id' in p]
        exclude_query = f"AND id NOT IN ({','.join(map(str, exclude_ids))})" if exclude_ids else ""

        # 💡 쿼리: 해당 카테고리만 정확히 타겟팅
        query = f"""
            SELECT * FROM products 
            WHERE category LIKE ? 
            {exclude_query}
            AND (product_spec LIKE ? OR ingredients LIKE '%진정%' OR ingredients LIKE '%병풀%')
            ORDER BY 
                (CASE WHEN ? = 1 AND (ingredients LIKE '%진정%' OR ingredients LIKE '%병풀%') THEN 0 ELSE 1 END) ASC,
                (CASE WHEN product_spec LIKE ? THEN 0 ELSE 1 END) ASC,
                RANDOM() 
            LIMIT 1
        """
        
        # search 키워드에 따라 검색 (예: '로션' 검색 시 '크림/로션'이 걸릴 수 있으므로 
        # 나중에 정렬이나 필터링으로 보정)
        cursor.execute(query, (f"%{item['search']}%", f"%{skin_type}%", 1 if is_sensitive else 0, f"%{skin_type}%"))
        row = cursor.fetchone()
        
        if row:
            p = dict(row)
            # 💡 화면에 표시될 카테고리명을 우리가 정한 Step 이름으로 고정!
            p['display_category'] = item['step']
            p['detail_url'] = p.get('detail_url', p.get('link', ''))
            p['is_wash_off'] = False
            products.append(p)

    conn.close()
    return products