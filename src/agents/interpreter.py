from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.agents.allergy_check import check_product_safety # 알레르기 체크 함수
from dotenv import load_dotenv
load_dotenv()
# 1. 모델 초기화 (API 키는 .env에 있다고 가정)
llm = ChatOpenAI(model="gpt-4o", temperature=0)
parser = JsonOutputParser()
# src/agents/interpreter.py 상단부

def get_consultation_prompt():
    """
    프롬프트 설계 함수 - JSON 중괄호를 {{ }}로 이스케이프 처리함
    """
    template = """
    당신은 SkinCare-Agent 시스템 내부에서 동작하는 피부 상태 해석 전용 LLM Agent입니다.

    ⚠️ 이 Agent는 사용자에게 직접 응답하지 않습니다.
    ⚠️ 제품 추천, DB 조회, 검색을 수행하지 않습니다.
    ⚠️ 오직 분석 결과를 해석하고 판단을 구조화하는 역할만 수행합니다.

    ---

    ### 당신의 임무
    이미지 분석 수치를 기반으로,
    다음 단계 시스템(LangGraph 노드)이 활용할 수 있도록
    피부 상태를 객관적이고 구조화된 판단 결과로 변환하세요.

    ---

    ## 입력 제공 정보
    - 홍조 점수: {redness}/100
    - 유분 점수: {oiliness}/100

    ---

    ### 판단 기준
    - 홍조: 70+(high), 40-70(medium), 40-(low)
    - 유분: 70+(high), 40-70(medium), 40-(low)

    ### 출력 스키마
    {{
     "skin_summary": "요약 문장",
     "skin_type": ["지성", "복합성", "건성", "민감성"], 
     "conditions": {{
        "redness": "low | medium | high",
        "oiliness": "low | medium | high"
     }},
    "care_priorities": ["진정", "보습"],
    "product_filter_hints": {{ "avoid": [], "prefer": [] }}
    }}

    입력 수치:
    - 홍조: {redness}, 유분: {oiliness}
    """
    return ChatPromptTemplate.from_template(template)

def generate_skin_report(redness, oiliness):
    prompt_template = get_consultation_prompt()
    chain = prompt_template | llm | parser
    return chain.invoke({"redness": redness, "oiliness": oiliness})

def generate_final_report(redness, oiliness, analysis_json, recommended_products, knowledge):
    # 1. 수치 기반 확정적 피부 타입 판정
    type_parts = []
    if oiliness < 30: type_parts.append("건성")
    elif oiliness > 70: type_parts.append("지성")
    else: type_parts.append("복합성")
    if redness > 50: type_parts.append("민감성")
    skin_type_str = " / ".join(type_parts)
    
    summary = analysis_json.get("skin_summary", "피부 분석 완료")
    care_priorities = list(analysis_json.get("care_priorities", []))
    llm_conditions = analysis_json.get("conditions", {})

    # 2. 상단 리포트 구성
    report = f"# 🔍 진단 결과: :blue[{skin_type_str}]\n"
    report += f"### 📝 {summary}\n"
    report += "--- \n\n"

    # 3. RAG 지식 섹션
    report += "### 📚 전문 지식 가이드 (RAG)\n"
    report += f"{knowledge}\n\n" # summarized_knowledge가 여기 들어갈 거임
    report += "--- \n\n"
    
    # 4. 상세 지표
    report += "#### 📊 상세 피부 지표\n"
    report += f"- **홍조 상태:** `{llm_conditions.get('redness', 'normal')}` ({redness}/100)\n"
    report += f"- **유분 상태:** `{llm_conditions.get('oiliness', 'normal')}` ({oiliness}/100)\n"
    report += f"- **관리 우선순위:** {', '.join([f'# {p}' for p in care_priorities]) if care_priorities else '#기본케어'}\n\n"

    # 5. 맞춤 추천 제품
    report += "### 🛍️ 맞춤 추천 제품 및 안전성 분석\n"
    
    if recommended_products:
        report += "| 카테고리 | 브랜드 | 제품명 | 가격 | 성분 안전성 |\n"
        report += "| :--- | :--- | :--- | :--- | :--- |\n"
        for p in recommended_products:
            category = p.get("category", "스킨케어")
            is_wash_off = "클렌징" in category
            safety_msg = check_product_safety(p.get("ingredients", ""), is_wash_off)
            p_url = p.get("detail_url") if p.get("detail_url") else f"https://search.shopping.naver.com/search/all?query={p['brand']}+{p['name']}"
            report += f"| {category} | {p['brand']} | [{p['name']}]({p_url}) | {p['price']}원 | {safety_msg} |\n"
    else:
        main_ingred = "병풀 판테놀" if redness > 50 else "히알루론산 세라마이드"
        def get_oy_url(cat, ingred):
            return f"https://www.oliveyoung.co.kr/store/search/getSearchMain.do?query={ingred}+{cat}"

        report += f"""
\n\n
<div style="background-color: #fff3cd; padding: 20px; border-radius: 10px; border: 1px solid #ffeeba; margin: 10px 0;">
    <h4 style="color: #856404; margin-top: 0;">⚠️ DB 매칭 제품을 찾지 못했습니다</h4>
    <p style="color: #666; font-size: 0.95em;">분석된 <b>{skin_type_str}</b> 피부 타입에 최적화된 올리브영 추천 상품 링크를 제공합니다.</p>
    <table style="width:100%; border-collapse: collapse; margin-top:10px; background-color: white; color: black;">
        <tr style="background-color: #f8f9fa;">
            <th style="padding:10px; border:1px solid #ddd;">카테고리</th>
            <th style="padding:10px; border:1px solid #ddd;">추천 성분 가이드</th>
            <th style="padding:10px; border:1px solid #ddd;">올리브영 바로가기</th>
        </tr>
        <tr>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;">💧 스킨/토너</td>
            <td style="padding:10px; border:1px solid #ddd;">결 정돈 및 진정 토너</td>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;"><a href="{get_oy_url('토너', main_ingred)}" target="_blank">🛒 이동</a></td>
        </tr>
        <tr>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;">🧪 세럼/앰플</td>
            <td style="padding:10px; border:1px solid #ddd;">고농축 집중 케어 앰플</td>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;"><a href="{get_oy_url('앰플', main_ingred)}" target="_blank">🛒 이동</a></td>
        </tr>
        <tr>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;">🧴 로션</td>
            <td style="padding:10px; border:1px solid #ddd;">유수분 밸런스 로션</td>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;"><a href="{get_oy_url('로션', main_ingred)}" target="_blank">🛒 이동</a></td>
        </tr>
        <tr>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;">🍦 크림</td>
            <td style="padding:10px; border:1px solid #ddd;">보습 장벽 강화 크림</td>
            <td style="padding:10px; border:1px solid #ddd; text-align:center;"><a href="{get_oy_url('크림', main_ingred)}" target="_blank">🛒 이동</a></td>
        </tr>
    </table>
</div>
\n\n
"""
    report += "\n---\n※ 본 결과는 AI 시각 분석 모델에 기반한 참고용 리포트입니다."
    
    # 💡 [핵심 해결 1] 리포트 문자열을 반드시 반환해야 함!
    return report

def summarize_knowledge(knowledge):
    if not knowledge or len(knowledge) < 20:
        return "관련된 전문 지식을 분석 중입니다."
    llm_summarizer = ChatOpenAI(model="gpt-4o", temperature=0)
    summary_prompt = f"당신은 뷰티 전문가입니다. 아래 내용을 3줄 요약하세요:\n\n{knowledge}"
    response = llm_summarizer.invoke(summary_prompt)
    return response.content

def interpreter_node(state):
    red = state.get("redness", 0)
    oil = state.get("oiliness", 0)
    products = state.get("recommended_products", [])
    raw_knowledge = state.get("skin_knowledge", "")

    # 1. AI 진단 JSON 생성
    analysis_json = generate_skin_report(red, oil)
    
    # 💡 [핵심 해결 2] 요약 함수를 실행해서 결과를 받아야 함!
    summarized = summarize_knowledge(raw_knowledge)
    
    # 💡 [핵심 해결 3] 5번째 인자로 요약된 지식을 넘겨줌!
    final_report = generate_final_report(red, oil, analysis_json, products, summarized)

    return {
        "analysis_result": analysis_json, 
        "final_report": final_report
    }