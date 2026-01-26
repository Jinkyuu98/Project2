# AI 피부 분석 & 화장품 추천

## 🧴 프로젝트 설명
이 프로젝트는 사용자의 피부 사진을 분석하여 피부 타입을 진단하고, 그에 맞는 맞춤형 화장품을 추천해주는 **Streamlit 기반 웹 애플리케이션**입니다.

가상의 AI 모델을 사용하여 피부 타입(지성, 건성, 복합성, 민감성)을 분석하고, 결과에 따라 적합한 스킨케어 제품을 제안합니다.

## ✨ 주요 기능
- **이미지 업로드**: 사용자의 얼굴 사진(JPG, PNG)을 업로드할 수 있습니다.
- **AI 피부 분석**: 업로드된 이미지를 분석하여 피부 타입과 신뢰도를 제공합니다.
- **화장품 추천**: 분석된 피부 타입에 맞는 스킨케어 제품(토너, 로션, 크림 등)을 추천합니다.

## 🛠️ 기술 스택
- **Python 3.x**
- **Streamlit**: 웹 인터페이스 구현
- **Pillow (PIL)**: 이미지 처리

## 🚀 설치 방법

1. **리포지토리 클론**
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **의존성 설치**
   ```bash
   pip install streamlit pillow
   ```

## 🏃 사용 방법

Streamlit 애플리케이션 실행:
```bash
streamlit run main.py
```

## 📂 프로젝트 구조
```
.
├── main.py                   # 메인 애플리케이션 진입점
├── services/
│   ├── skin_analyzer.py      # 피부 분석 로직 (시뮬레이션)
│   └── recommender.py        # 화장품 추천 로직
└── README.md                 # 프로젝트 문서
```
