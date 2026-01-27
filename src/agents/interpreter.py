from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 모델 초기화 (API 키는 .env에 있다고 가정)
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
parser = StrOutputParser()

def get_consultation_prompt():
    """
    조원 C가 가장 공들여야 할 프롬프트 설계 함수
    """
    template = """
    당신은 피부과 전문의 AI 상담사입니다. 
    제공된 데이터와 제품 정보를 바탕으로 환자에게 맞춤형 진단을 내려주세요.

    [실시간 피부 분석 수치]
    - 홍조 점수: {redness}/100 (높을수록 붉음)
    - 유분 점수: {oiliness}/100 (높을수록 번들거림)

    [추천 제품 리스트]
    {products}

    [답변 필수 포함 내용]
    1. 현재 피부 상태에 대한 전문적인 총평 (마크다운 제목 # 사용)
    2. 수치에 기반한 구체적인 피부 문제점 분석
    3. 추천된 제품들을 써야 하는 이유 (성분과 수치를 연결해서 설명)
    4. 일상 속에서 실천할 피부 관리 팁 1가지

    답변은 신뢰감 있고 친절한 말투로 작성해 주세요.
    """
    return ChatPromptTemplate.from_template(template)

def generate_skin_report(redness, oiliness, products):
    """
    팀장님이 나중에 통합(Main) 파일에서 호출할 메인 함수
    """
    prompt_template = get_consultation_prompt()
    
    # 랭체인 LCEF 구조: 프롬프트 -> 모델 -> 출력 파서
    chain = prompt_template | llm | parser
    
    # 실제 AI 실행
    response = chain.invoke({
        "redness": redness,
        "oiliness": oiliness,
        "products": products
    })
    
    return response

# --- 여기서부터는 테스트용 (실행 시에만 동작) ---
if __name__ == "__main__":
    # 테스트 데이터
    sample_red = 82.9
    sample_oil = 29.3
    sample_items = "1. 아누아 어성초 토너 (진정 효과) \n2. 닥터자르트 시카페어 크림 (장벽 강화)"
    
    print("🚀 상담 생성 중...")
    result = generate_skin_report(sample_red, sample_oil, sample_items)
    print("-" * 30)
    print(result)