import sqlite3
import pandas as pd
import os

# 1. DB 경로 설정 (make_db.py에서 생성된 경로와 맞춰줘)
# 현재 위치가 Project2/project2라면 아래와 같이 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.abspath(os.path.join(current_dir, "../../db/skin_products.db"))

print(f"🔍 DB 경로 확인 중: {db_path}")

if not os.path.exists(db_path):
    print("❌ DB 파일을 찾을 수 없어! 경로를 다시 확인해봐.")
else:
    conn = sqlite3.connect(db_path)
    
    print("\n📊 [1. 카테고리별 상품 개수]")
    query_count = "SELECT category, COUNT(*) as count FROM products GROUP BY category"
    df_count = pd.read_sql_query(query_count, conn)
    print(df_count)
    
    print("\n✨ [2. 데이터 샘플 (상위 5개)]")
    query_sample = "SELECT category, brand, name, price FROM products LIMIT 5"
    df_sample = pd.read_sql_query(query_sample, conn)
    print(df_sample)
    
    conn.close()
    print("\n✅ 확인 완료!")