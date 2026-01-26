def recommend_products(skin_type):
    dummy_products = {
        "지성": [
            {"name": "산뜻 토너 A", "category": "토너"},
            {"name": "유분 컨트롤 로션 B", "category": "로션"}
        ],
        "건성": [
            {"name": "고보습 크림 C", "category": "크림"},
            {"name": "히알루론 에센스 D", "category": "에센스"}
        ],
        "복합성": [
            {"name": "밸런스 토너 E", "category": "토너"},
            {"name": "수분 젤 크림 F", "category": "크림"}
        ],
        "민감성": [
            {"name": "저자극 토너 G", "category": "토너"},
            {"name": "시카 크림 H", "category": "크림"}
        ]
    }

    return dummy_products.get(skin_type, [])
