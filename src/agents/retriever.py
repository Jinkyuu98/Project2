from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 저장할 때 썼던 세팅 그대로!
PERSIST_DIR = r"src\database"
COLLECTION_NAME = "skin_blog_docs"
EMBEDDING_MODEL = "intfloat/multilingual-e5-base"

def get_relevant_knowledge(query: str, k: int = 3):
    """Vector DB에서 쿼리와 관련된 지식 상위 k개를 가져옴"""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # 1. DB 로드
    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )
    
    # 2. 유사도 검색 (Similarity Search)
    docs = vectordb.similarity_search(query, k=k)
    
    # 3. 검색된 내용을 하나의 텍스트로 합치기
    knowledge_text = "\n\n".join([doc.page_content for doc in docs])
    return knowledge_text