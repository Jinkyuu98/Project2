import hashlib
import requests
import trafilatura
from bs4 import BeautifulSoup

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

PERSIST_DIR = r"src\database"     # 저장 경로 지정 
COLLECTION_NAME = "skin_blog_docs"
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"

def normalize_url(url: str) -> str:
    # ✅ 네이버 블로그는 모바일 페이지가 본문 추출이 훨씬 잘 됨
    if url.startswith("https://blog.naver.com/"):
        return url.replace("https://blog.naver.com/", "https://m.blog.naver.com/")
    return url


def fetch_html(url: str, timeout: int = 15) -> str:
    """URL에서 HTML 다운로드 (실패하면 예외)"""
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    }
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    # ✅ 한글 깨짐 방지: requests가 인코딩을 잘못 잡는 경우가 많아서 보정
    r.encoding = r.apparent_encoding
    return r.text


def extract_main_text(html: str) -> str:
    """
    HTML에서 본문 텍스트만 추출.
    1) trafilatura로 본문 추출을 우선 시도
    2) 실패하면 BeautifulSoup로 전체 텍스트 fallback
    """
    # ✅ allow_fallback 옵션 제거 (버전 호환)
    text = trafilatura.extract(html, include_comments=False, include_tables=True)
    if text and len(text.strip()) > 10:
        return text.strip()

    # fallback: soup.get_text()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return text.strip()


def extract_title(html: str) -> str:
    """HTML에서 title 태그 추출"""
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    return title


def url_to_doc(url: str, category: str = "skin_care") -> Document:
    """
    URL 1개 → Document 1개
    metadata에 url/title/category 등을 저장 (나중에 필터/출처표시에 매우 유리)
    """
    url = normalize_url(url)  # ✅ 추가

    html = fetch_html(url)
    text = extract_main_text(html)
    title = extract_title(html)

    if len(text) < 10:
        raise ValueError(f"본문 텍스트가 너무 짧습니다(추출 실패 가능): {url}")

    return Document(
        page_content=text,
        metadata={
            "source": "web",
            "url": url,
            "title": title,
            "category": category,
            "text_len": len(text),
        }
    )


def build_chroma_from_urls(
    urls_with_category,
    persist_dir: str = PERSIST_DIR,            # ✅ 기본값을 절대경로로 고정
    collection_name: str = COLLECTION_NAME,    # ✅ 고정
):
    ...
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)  # ✅ 고정
    ...
    vectordb = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    raw_docs = []
    for item in urls_with_category:
        url = item["url"]
        category = item.get("category", "skin_care")
        try:
            doc = url_to_doc(url, category=category)
            raw_docs.append(doc)
            print(f"[OK] {category} | {doc.metadata.get('title','')[:40]} | len={doc.metadata.get('text_len')} | {url}")
        except Exception as e:
            print(f"[SKIP] {url} | {type(e).__name__}: {e}")

    if not raw_docs:
        raise RuntimeError("수집된 문서가 없습니다. URL/추출을 점검하세요.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunk_docs = splitter.split_documents(raw_docs)
    print(f"원문 {len(raw_docs)}개 → 청크 {len(chunk_docs)}개")

    embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

    ids = []
    for d in chunk_docs:
        base = f"{d.metadata.get('url','')}|{d.page_content[:200]}"
        ids.append(hashlib.md5(base.encode("utf-8")).hexdigest())

    vectordb = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )
    vectordb.add_documents(chunk_docs, ids=ids)
    vectordb.persist()

    print(f"✅ Chroma 저장 완료: {persist_dir} (collection={collection_name})")
    return vectordb


# 사용 예시
urls_with_category = [
    {"url": "https://blog.naver.com/media666/224160518265", "category": "skin_care"},
    {"url": "https://jopingping.tistory.com/3", "category": "skin_care"},
    {"url": "https://makebeauty.tistory.com/256", "category": "skin_care"},
    {"url": "https://jinjji0910.tistory.com/218", "category": "skin_care"},
    {"url": "https://curatorshop.tistory.com/154", "category": "skin_care"},
    {"url": "https://kkkamiu.tistory.com/4", "category": "skin_care"},
    {"url": "https://curatorshop.tistory.com/72", "category": "skin_care"},
    {"url": "https://isthereanything.tistory.com/7", "category": "skin_care"},
    {"url": "https://smbdi.com/entry/%EB%82%A8%EC%9E%90-%EC%A7%80%EC%84%B1-%ED%94%BC%EB%B6%80-%EC%8A%A4%ED%82%A8-%EB%A1%9C%EC%85%98-%EC%B6%94%EC%B2%9C-%EC%88%9C%EC%9C%84-TOP-7-%EB%84%A4%EC%9D%B4%EB%B2%84-%EC%BF%A0%ED%8C%A1-%EC%98%AC%EB%A6%AC%EB%B8%8C%EC%98%81-%ED%8C%90%EB%A7%A4-%EB%B6%84%EC%84%9D","category": "skin_care"},
    {"url": "https://www.chemidream.com/2030", "category": "skin_care"},
    {"url": "https://topfour.tistory.com/98", "category": "skin_care"},
    {"url": "https://m.blog.naver.com/mk0414578/223351227239", "category": "skin_care"},
    {"url": "https://todaybeauty.tistory.com/v/246", "category": "skin_care"},
    {"url": "https://planner-cho.tistory.com/entry/%EB%AF%BC%EA%B0%90-%ED%94%BC%EB%B6%80%EB%A5%BC-%EC%9C%84%ED%95%9C-%EC%84%B1%EB%B6%84-3%EA%B0%80%EC%A7%80-%EB%B3%91%ED%92%80-%ED%8C%90%ED%85%8C%EB%86%80-%EC%96%B4%EC%84%B1%EC%B4%88-%EB%B9%84%EA%B5%90", "category": "skin_care"},
    {"url": "https://news.hidoc.co.kr/news/articleView.html?idxno=136769", "category": "skin_care"},
    {"url": "https://delimanjoo.tistory.com/111", "category": "skin_care"},
    {"url": "https://unpa.me/community/unniepick/119897788", "category": "skin_care"},
    {"url": "https://dororo-ordinary.tistory.com/entry/%ED%94%BC%EB%B6%80%ED%83%80%EC%9E%85%EB%B3%84-%EA%B8%B0%EC%B4%88%ED%99%94%EC%9E%A5%ED%92%88-%EC%B6%94%EC%B2%9C-%E2%80%93-%EB%82%B4-%ED%94%BC%EB%B6%80%EC%97%90-%EB%A7%9E%EB%8A%94-%EC%8A%A4%ED%82%A8%EC%BC%80%EC%96%B4", "category": "skin_care"},
    {"url": "https://blog.naver.com/brainpi/221708865226", "category": "skin_care"},
    {"url": "https://myblogbeauvique.tistory.com/1", "category": "skin_care"},
    {"url": "https://ckdals331.tistory.com/entry/%F0%9F%92%962025-%EB%B0%94%EC%9D%B4%EC%98%A4%EB%8D%94%EB%A7%88-%EC%B6%94%EC%B2%9C%ED%85%9C-BEST-5-%E2%80%93-%ED%94%BC%EB%B6%80%ED%83%80%EC%9E%85%EB%B3%84-%ED%9B%84%EA%B8%B0%EA%B0%80%EA%B2%A9-%EC%B4%9D%EC%A0%95%EB%A6%AC%F0%9F%92%96", "category": "skin_care"},
    {"url": "https://reviewpro.co.kr/best-moisturizing-cream/", "category": "skin_care"},
    {"url": "https://blog.naver.com/freshvieco/220841759458/", "category": "skin_care"},
    {"url": "https://m.blog.naver.com/mongkonge/223690372574", "category": "skin_care"},
    {"url": "https://m.blog.naver.com/brainpi/221580927405", "category": "skin_care"},
    {"url": "https://m.blog.naver.com/volume4376/223770947005", "category": "skin_care"},
    {"url": "https://blog.naver.com/615232/223746454707?trackingCode=rss", "category": "skin_care"},
    {"url": "https://hamme.tistory.com/220", "category": "skin_care"},
    {"url": "https://ideas4646.tistory.com/70", "category": "skin_care"},
    {"url": "https://trangcosmetic.tistory.com/entry/%EB%8B%A4%EC%96%91%ED%95%9C-%ED%94%BC%EB%B6%80-%ED%83%80%EC%9E%85%EC%97%90-%EB%94%B0%EB%A5%B8-%EC%95%8C%EB%A7%9E%EC%9D%80-%ED%99%94%EC%9E%A5%ED%92%88-%EC%B6%94%EC%B2%9C", "category": "skin_care"},
    {"url": "https://mystory8956.tistory.com/104", "category": "skin_care"},
    {"url": "https://conishaskincare.tistory.com/53", "category": "skin_care"},
    {"url": "https://beautyfly.tistory.com/entry/%EC%A7%80%EC%84%B1-%EA%B1%B4%EC%84%B1-%EB%B3%B5%ED%95%A9%EC%84%B1-%EC%88%98%EB%B6%80%EC%A7%80-%ED%94%BC%EB%B6%80-%EA%B4%80%EB%A6%AC-%EB%B0%A9%EB%B2%95", "category": "skin_care"},
    {"url": "https://rippleaananchor.tistory.com/entry/%EB%82%A8%EC%9E%90-%EC%8A%A4%ED%82%A8-%EC%BC%80%EC%96%B4-%EC%99%84%EB%B2%BD-%EA%B0%80%EC%9D%B4%EB%93%9C-%ED%94%BC%EB%B6%80-%ED%83%80%EC%9E%85%EB%B3%84-%EA%BF%80%ED%8C%81%EA%B3%BC-%EC%B6%94%EC%B2%9C-%EC%A0%9C%ED%92%88", "category": "skin_care"},
    {"url": "https://health-doctor.tistory.com/entry/%EB%82%9C-%EC%A7%80%EC%84%B1%EC%9D%B4%EC%95%BC-%EA%B1%B4%EC%84%B1%EC%9D%B4%EC%95%BC-%EA%B0%84%EB%8B%A8%ED%95%98%EA%B2%8C-%ED%94%BC%EB%B6%80-%ED%83%80%EC%9E%85-%EC%95%8C%EC%95%84%EB%B3%B4%EA%B8%B0", "category": "skin_care"},
    {"url": "https://lovereport.net/70", "category": "skin_care"},
    {"url": "https://happy4860.tistory.com/216", "category": "skin_care"},
    {"url": "https://toto-bg.com/11", "category": "skin_care"},
    {"url": "https://jjjjjiiiii.tistory.com/25", "category": "skin_care"},
    {"url": "https://mzmi.tistory.com/entry/%EC%98%AC%EB%A6%AC%EB%B8%8C%EC%98%81-%EB%A7%88%EC%8A%A4%ED%81%AC%ED%8C%A9-%EC%B6%94%EC%B2%9C-%EA%B1%B4%EC%84%B1%ED%94%BC%EB%B6%80-%EB%B3%B5%ED%95%A9%EC%84%B1-%ED%94%BC%EB%B6%80-%EC%A7%80%EC%84%B1%ED%94%BC%EB%B6%80-%ED%83%80%EC%9E%85%EB%B3%84-%EB%A7%88%EC%8A%A4%ED%81%AC%ED%8C%A9-%EC%B6%94%EC%B2%9C", "category": "skin_care"},
    {"url": "https://dolnsoo.tistory.com/entry/%EB%8B%A4%EC%9D%B4%EC%86%8C-%EC%84%A0%ED%81%AC%EB%A6%BC-%EC%B6%94%EC%B2%9C-%EC%A7%80%EC%84%B1%EA%B1%B4%EC%84%B1-%ED%94%BC%EB%B6%80-%ED%83%80%EC%9E%85%EB%B3%84-%EA%B4%9C%EC%B0%AE%EC%9D%80-%EC%84%A0%ED%81%AC%EB%A6%BC-%EC%B6%94%EC%B2%9C", "category": "skin_care"},
    {"url": "https://myview25426.tistory.com/9", "category": "skin_care"},
    {"url": "https://blog.naver.com/ssi_000/223446494469", "category": "skin_care"},
]

db = build_chroma_from_urls(
    urls_with_category,
    persist_dir=PERSIST_DIR,
    collection_name=COLLECTION_NAME
)
print("✅ 저장된 문서 개수:", db._collection.count())
print("✅ 저장 경로:", PERSIST_DIR)