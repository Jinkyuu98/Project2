# 🩺 SkinCare-Agent: 맞춤형 피부 건강관리 AI 에이전트

> **"사진 한 장으로 시작하는 퍼스널 헬스케어"** > 사용자의 피부 상태를 분석하고, 알러지 성분을 고려한 최적의 화장품을 추천하며 구매까지 연결하는 LangGraph 기반의 지능형 에이전트입니다.

---

## 🌟 주요 기능 (Key Features)

- **[Vision] 정밀 피부 분석**: Mediapipe를 활용해 피부의 홍조, 유분, 트러블 상태를 수치화합니다.
- **[LangGraph] 지능형 워크플로우**: 상태 노드 설계를 통해 분석, 검색, 필터링 과정을 유연하게 제어합니다.
- **[Hybrid RAG] 맞춤형 검색**: 올리브영 크롤링 데이터와 실시간 리뷰를 결합하여 사용자 피부 타입에 최적화된 제품을 제안합니다.
- **[Safety] 세이프티 가드레일**: 사용자의 알러지 성분을 SQL DB와 대조하여 부작용 없는 제품만 최종 선별합니다.
- **[Agent Action] 커머스 연결**: 분석 리포트 제공 및 제품 구매 페이지로 즉시 연결되는 인터페이스를 제공합니다.

---

## 🛠 기술 스택 (Tech Stack)

### AI & Framework
- **Orchestration**: LangGraph, LangChain
- **LLM**: OpenAI GPT-4o
- **Vision**: Google Mediapipe, OpenCV

### Data & Storage
- **Vector DB**: ChromaDB (비정형 리뷰 및 제품 효능 데이터)
- **RDBMS**: SQLite (제품 전성분 및 알러지 기준 데이터)
- **Crawling**: BeautifulSoup, Selenium

### Frontend & Infrastructure
- **UI**: Streamlit
- **Environment**: Docker, Docker Compose

---

## 📂 프로젝트 구조 (Project Structure)
```
Project2/
├── venv/                    # 파이썬 가상환경 (Docker 대신 사용)
├── data/                    # 데이터 저장소 (Vector DB, SQLite)
├── src/                     # 핵심 소스 코드
│   ├── graph/               # LangGraph 워크플로우 정의
│   ├── engine/              # Vision 분석 및 RAG 검색 엔진
│   └── main.py              # Streamlit 실행 파일
├── .env                     # API KEY 관리
└── requirements.txt         # 설치 라이브러리 목록
```

---

## 🚀 시작하기 (Quick Start)

1. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

2. **필수 라이브러리 설치**
   ```pip install -r requirements.txt```

3. **애플리케이션 실행**
   ```streamlit run src/main.py```
