import pandas as pd
import sqlite3
import os

# 1. 절대 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(current_dir, "../../"))
DATA_DIR = os.path.join(BASE_DIR, "data_files")
DB_DIR = os.path.join(BASE_DIR, "db")

# 2. 통합 리스트 (명칭을 '스킨/토너', '크림' 등으로 명확히 수정)
file_configs = [
    {"file": "oliveyoung_skin_toner_v1_2_v0_6_clean.csv", "display_cat": "스킨/토너"},
    {"file": "oliveyoung_cream_v1_0_v0_6_clean.csv", "display_cat": "크림"},
    {"file": "oliveyoung_lotion_v1_0_v0_6_clean.csv", "display_cat": "로션"},
    {"file": "oliveyoung_serum_ampoule_v1_1_v0_6_clean.csv", "display_cat": "에센스/세럼/앰플"}
]

all_dfs = []

print(f"🚀 중복 제거 및 카테고리 최적화 시작...")

for config in file_configs:
    f_path = os.path.join(DATA_DIR, config["file"])
    if os.path.exists(f_path):
        df = pd.read_csv(f_path, encoding='utf-8-sig')
        
        # 카테고리 강제 부여
        df['category'] = config["display_cat"]
        
        # 가격 정제
        df['price'] = df['price'].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
        
        # 성분 공백 제거 (알레르기 필터링 정확도 향상)
        if 'ingredients' in df.columns:
            df['ingredients'] = df['ingredients'].astype(str).str.replace(' ', '').str.replace('\n', '')

        all_dfs.append(df)
        print(f"✅ {config['file']} 로드 완료")

if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    
    # 🔥 [중복 제거의 핵심] 상품명이 같으면 첫 번째 것만 남기고 삭제
    before_count = len(final_df)
    final_df = final_df.drop_duplicates(subset=['name'], keep='first')
    after_count = len(final_df)
    
    print(f"💡 중복 상품 {before_count - after_count}개를 제거했습니다.")

    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    db_path = os.path.join(DB_DIR, "skin_products.db")
    conn = sqlite3.connect(db_path)
    final_df.to_sql("products", conn, if_exists="replace", index=False)
    conn.close()
    
    print("-" * 40)
    print(f"🎉 DB 생성 완료! (총 {len(final_df)}개 고유 상품)")
    print(f"📂 경로: {db_path}")