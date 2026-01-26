import streamlit as st
from PIL import Image
from services.skin_analyzer import analyze_skin
from services.recommender import recommend_products

st.set_page_config(page_title="AI 피부 분석", layout="centered")

st.title("🧴 AI 피부 분석 & 화장품 추천")

st.write("피부 사진을 업로드하면 피부 타입을 분석하고 맞춤 화장품을 추천해줘요.")

uploaded_file = st.file_uploader(
    "피부 사진을 업로드하세요",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)

    st.subheader("📷 업로드한 이미지")
    st.image(image, width=300)

    if st.button("피부 분석 시작"):
        with st.spinner("피부 분석 중..."):
            skin_result = analyze_skin(image)

        st.subheader("🧬 피부 분석 결과")
        st.write(f"**피부 타입:** {skin_result['skin_type']}")
        st.write(f"**신뢰도:** {skin_result['confidence']}%")

        st.subheader("🛍 추천 화장품")
        products = recommend_products(skin_result["skin_type"])

        for p in products:
            st.markdown(f"- **{p['name']}** ({p['category']})")
