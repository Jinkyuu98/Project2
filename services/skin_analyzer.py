import random

def analyze_skin(image):
    """
    image: PIL Image
    return: dict
    """
    skin_types = ["지성", "건성", "복합성", "민감성"]

    return {
        "skin_type": random.choice(skin_types),
        "confidence": random.randint(80, 95)
    }
