graph TD
    %% 시작점
    Start((유저 입력)) --> Intent[<b>1. Intent Analysis Node</b><br/>채팅에서 알러지 성분 & 고민 추출]
    
    %% 분석 단계
    Intent --> Vision[<b>2. Vision Analysis Node</b><br/>피부 사진에서 유분/홍조 수치화]
    Vision --> Verify[<b>3. Logic Verification Node</b><br/>가중 평균 로직으로 수치 보정]
    
    %% 검색 및 매칭 단계
    Verify --> Retriever[<b>4. Knowledge Retriever</b><br/>RAG 기반 피부 전문 지식 검색]
    Retriever --> DB[<b>5. Database Search Node</b><br/>알러지 필터링 & 가성비 제품 매칭]
    
    %% 결과 생성
    DB --> Interpreter[<b>6. Report Interpreter</b><br/>브랜드명 정리 및 맞춤형 리포트 생성]
    Interpreter --> End((최종 리포트 발행))

    %% 스타일링
    style Intent fill:#f9f,stroke:#333,stroke-width:2px
    style Vision fill:#bbf,stroke:#333,stroke-width:2px
    style DB fill:#bfb,stroke:#333,stroke-width:2px
    style Interpreter fill:#fbb,stroke:#333,stroke-width:4px