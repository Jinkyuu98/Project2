import pandas as pd
import sqlite3
import os

# 1. 절대 경로 기준 설정
# __file__은 현재 이 파일(make_db.py)의 위치를 말해.
# .parent를 두 번 하면 src/scripts -> src -> Project2(루트)로 올라가게 돼.
current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(current_dir, "../../")) # Project2 루트 폴더

# 2. 하위 폴더 경로 정의
DATA_DIR = os.path.join(BASE_DIR, "data_files") # CSV 파일들이 모여있는 곳
DB_DIR = os.path.join(BASE_DIR, "db")           # DB가 저장될 곳

# 3. 통합할 파일 리스트
file_configs = [
    {"file": "oliveyoung_skin_toner_v1_2_v0_6_clean.csv", "display_cat": "토너/패드"},
    {"file": "oliveyoung_cream_v1_0_v0_6_clean.csv", "display_cat": "크림/로션"},
    {"file": "oliveyoung_lotion_v1_0_v0_6_clean.csv", "display_cat": "로션"},
    {"file": "oliveyoung_serum_ampoule_v1_1_v0_6_clean.csv", "display_cat": "에센스/세럼"}
]

all_dfs = []

print(f"📂 데이터 폴더 위치: {DATA_DIR}")
print("🚀 데이터 통합 및 DB 생성 시작...")

# 4. 파일 읽기 및 전처리
for config in file_configs:
    f_path = os.path.join(DATA_DIR, config["file"])
    
    if os.path.exists(f_path):
        df = pd.read_csv(f_path, encoding='utf-8-sig')
        
        # 컬럼명 정리 및 카테고리 부여
        if "Unnamed: 2" in df.columns:
            df.rename(columns={"Unnamed: 2": "category_raw"}, inplace=True)
        df['category'] = config["display_cat"]
        
        # 가격 데이터 숫자형으로 변환
        df['price'] = df['price'].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
        
        all_dfs.append(df)
        print(f"✅ {config['file']} 로드 성공")
    else:
        # ⚠️ 여기서 파일이 없으면 팀장님 터미널에 에러가 뜰 거야.
        print(f"❌ 파일을 찾을 수 없음: {f_path}")

# 5. DB 저장
if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    db_path = os.path.join(DB_DIR, "skin_products.db")
    conn = sqlite3.connect(db_path)
    final_df.to_sql("products", conn, if_exists="replace", index=False)
    conn.close()
    
    print("-" * 40)
    print(f"🎉 DB 생성 완료! 총 {len(final_df)}개 상품이 저장되었습니다.")
    print(f"📂 DB 경로: {db_path}")
else:
    print("❌ 통합할 수 있는 데이터 파일이 없습니다. data_files 폴더를 확인해주세요!")