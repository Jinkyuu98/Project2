# src/database/sqlite_db.py
import sqlite3
import os

# DB 경로 (Project2/db/skin_products.db)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "db", "skin_products.db")

def get_recommended_products(oiliness, redness, limit=3):
    if not os.path.exists(DB_PATH):
        print(f"❌ DB 파일을 찾을 수 없음: {DB_PATH}")
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. 피부 타입 및 상태에 따른 키워드 설정
    skin_type = "지성" if oiliness > 50 else "건성"
    # 홍조가 높으면 '진정' 성분 우선 검색
    condition = "AND ingredients LIKE '%진정%'" if redness > 50 else ""

    # 2. 쿼리 실행 (product_spec에 피부타입이 포함된 것 중 랜덤 추출)
    query = f"""
        SELECT * FROM products 
        WHERE product_spec LIKE ? 
        {condition}
        ORDER BY RANDOM() 
        LIMIT ?
    """
    cursor.execute(query, (f"%{skin_type}%", limit))
    rows = cursor.fetchall()
    
    products = []
    for row in rows:
        p = dict(row)
        # 지수님 가이드에 맞게 키값 매핑 (detail_url -> link)
        p['link'] = p.get('detail_url', '')
        # 카테고리가 클렌징이면 세정제(wash_off)로 표시
        p['is_wash_off'] = True if "클렌징" in p.get('category', '') else False
        products.append(p)

    conn.close()
    return products