# 🩺 SkinCare-Agent: 맞춤형 피부 건강관리 AI 에이전트

> **"사진 한 장으로 시작하는 퍼스널 헬스케어"**
> 사용자의 피부 상태를 정밀 분석하고, 조명 환경 검증 및 블로그 RAG 기반 지식 검색을 통해 최적의 화장품을 추천하는 LangGraph 기반 지능형 에이전트입니다.

---

## 🌟 주요 기능 (Key Features)

- **[Vision] 정밀 피부 분석**: Mediapipe와 OpenCV를 활용하여 피부의 홍조(Redness), 유분(Oiliness), 트러블 상태를 객관적 수치로 산출합니다.
- **[Verification] 조명 환경 판독 (New)**: `verify` 노드를 통해 촬영 환경의 조명 상태를 분석하고, 데이터의 신뢰성을 검증하여 분석 결과의 정확도를 높입니다.
- **[LangGraph] 지능형 워크플로우**: `Vision -> Verify -> Retriever -> Database -> Interpreter` 단계로 이어지는 유연하고 안정적인 에이전트 워크플로우를 구현했습니다.
- **[Hybrid RAG] 고도화된 지식 검색**: `item.py`를 통해 네이버/티스토리 등 전문 블로그 데이터를 크롤링하여 구축한 ChromaDB 지식 베이스를 바탕으로 최적의 스킨케어 팁을 제공합니다.
- **[Safety] 맞춤 성분 필터링**: 사용자의 알러지 성분을 SQLite DB와 대조하여 부작용 위험이 없는 안전한 제품군만 엄격히 선별합니다.
- **[Final Report] 종합 분석 리포트**: 분석 수치, 지식 검색 기반 가이드, 맞춤 제품 추천이 포함된 마크다운 형식의 시각적 리포트를 자동 생성합니다.

---

## 🛠 기술 스택 (Tech Stack)

### AI & Framework
- **Orchestration**: LangGraph, LangChain
- **LLM**: OpenAI GPT-4o
- **Vision**: Google Mediapipe, OpenCV

### Data & Search
- **Vector DB**: ChromaDB (블로그 포스트 기반 비정형 데이터 검색)
- **RDBMS**: SQLite (제품 전성분 및 알러지 정보 관리)
- **Data Ingestion**: BeautifulSoup, Trafilatura (`item.py`)
- **Embeddings**: HuggingFace (`multilingual-e5-base`)

### Web UI
- **Frontend**: Streamlit

---

## 📂 프로젝트 구조 (Project Structure)

```
Project2/
├── data/                    # DB 저장소 (ChromaDB, SQLite)
├── data_files/              # 크롤링된 올리브영 제품 원본 CSV
├── src/                     # 핵심 소스 코드
│   ├── agents/              # 검색(Retriever), 성분 체크 등 에이전트 로직
│   ├── database/            # SQL DB 연결 및 ChromaDB 관리
│   ├── engine/              # 비전 분석 모델 및 핵심 엔진
│   ├── graph/               # LangGraph 워크플로우, 상태(State), 노드(Nodes) 정의
│   ├── scripts/             # DB 구축 및 점검용 유틸리티 스크립트
│   └── main.py              # Streamlit 웹 어플리케이션 실행 파일
├── item.py                  # 블로그 데이터 크롤링 및 벡터 DB 구축 스크립트
├── .env                     # API KEY 및 환경 설정
└── requirements.txt         # 종속성 라이브러리 목록
```

---

## 🚀 시작하기 (Quick Start)

1. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

2. **필수 라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```

3. **데이터베이스 구축 (필요 시)**
   ```bash
   # 블로그 데이터 벡터화 (item.py 수정 후 실행)
   python item.py
   # SQLite 데이터 베이스 생성
   python src/scripts/make_db.py
   ```

4. **애플리케이션 실행**
   ```bash
   streamlit run src/main.py
   ```

---

## 📸 분석 결과 예시 (Sample Result)
- 에이전트는 이미지 분석 후 실시간으로 유분/홍조 수치를 대시보드에 표시하며, 하단에 생성된 상세 분석 리포트를 통해 개인화된 솔루션을 제공합니다.
