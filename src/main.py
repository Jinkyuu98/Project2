import streamlit as st
import time

# 1. 페이지 설정
st.set_page_config(page_title="SkinCare Agent", page_icon="🩺", layout="centered")

# 2. 제목 및 소개
st.title("🩺 퍼스널 피부 헬스케어 에이전트")
st.markdown("---")

# 3. 사이드바 - 유저 정보 입력
with st.sidebar:
    st.header("👤 유저 프로필")
    user_allergy = st.multiselect(
        "알러지 성분을 선택하세요",
        ["페녹시에탄올", "파라벤", "향료", "에탄올", "미네랄 오일"]
    )
    skin_concern = st.selectbox(
        "주요 피부 고민",
        ["여드름/트러블", "홍조/민감성", "기미/잡티", "건조함/탄력저하"]
    )

# 4. 메인 화면 - 이미지 업로드
st.subheader("📸 피부 사진 분석")
uploaded_file = st.file_uploader("피부 사진을 찍거나 업로드하세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 사진 미리보기
    st.image(uploaded_file, caption="업로드된 사진", use_container_width=True)
    
    if st.button("에이전트에게 분석 요청하기"):
        with st.status("에이전트가 분석 중입니다...", expanded=True) as status:
            # Step 1: Vision 분석 (Mediapipe 노드 시뮬레이션)
            st.write("🔍 Mediapipe로 피부 영역 분석 중...")
            time.sleep(1)
            
            # Step 2: LangGraph 쿼리 생성
            st.write("🧠 분석 수치를 기반으로 맞춤 쿼리 생성 중...")
            time.sleep(1)
            
            # Step 3: RAG 검색 및 SQL 필터링
            st.write("📚 올리브영 데이터베이스에서 최적의 제품 검색 중...")
            time.sleep(1)
            
            # Step 4: 알러지 체크 (Safety Guardrail)
            st.write(f"🛡️ 선택하신 알러지({', '.join(user_allergy)}) 성분 필터링 중...")
            time.sleep(1)
            
            status.update(label="분석 완료!", state="complete", expanded=False)

        st.success("✅ 분석이 완료되었습니다!")

        # 5. 결과 리포트 출력 (가상의 결과)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="유분 수치", value="75%", delta="지성")
        with col2:
            st.metric(label="홍조 수치", value="15%", delta="-5% (정상)", delta_color="normal")

        st.subheader("✨ 추천 제품 리포트")
        
        # 가상의 추천 제품 리스트 (RAG 결과물 예시)
        products = [
            {"name": "토리든 다이브인 수분크림", "reason": "지성 피부에 적합한 가벼운 제형", "link": "https://www.oliveyoung.co.kr/"},
            {"name": "닥터지 레드 블레미쉬 크림", "reason": "민감성 및 여드름성 피부 진정 효과", "link": "https://www.oliveyoung.co.kr/"}
        ]

        for p in products:
            with st.expander(f"🛒 {p['name']}"):
                st.write(f"**추천 이유:** {p['reason']}")
                st.link_button("구매 페이지로 이동", p['link'])

else:
    st.info("왼쪽 사이드바에서 정보를 입력하고 피부 사진을 업로드해주세요.")