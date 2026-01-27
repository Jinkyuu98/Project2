import os
from pathlib import Path
from src.engine.vision_model import SkinAnalyzer
import sys
print(f"현재 실행 중인 파이썬 경로: {sys.executable}")
def main():
    # 1. 경로 설정 (윈도우에서도 안전하게)
    base_path = Path(__file__).parent
    image_path = base_path / "data" / "sample_image.jpg"
    
    # 2. 이미지 존재 확인
    if not image_path.exists():
        print(f"❌ 파일을 찾을 수 없어: {image_path}")
        print("data 폴더에 sample_face.jpg 파일을 넣어줘!")
        return

    # 3. 분석기 초기화 및 실행
    analyzer = SkinAnalyzer()
    print(f"🔍 분석 중: {image_path.name}...")
    
    try:
        # 문자열 경로로 변환해서 전달
        result = analyzer.analyze_process(str(image_path))
        
        if result["status"] == "success":
            print("\n" + "="*30)
            print("✅ 분석 결과 리포트")
            print("-" * 30)
            print(f"🌡️ 홍조 수치: {result['metrics']['redness_level']} (높을수록 붉음)")
            print(f"✨ 유분 수치: {result['metrics']['oiliness_level']} (높을수록 번들거림)")
            print("="*30)
            
            # 상세 데이터 확인용
            # print(f"DEBUG: {result['raw_data']}") 
            
        else:
            print(f"❌ 분석 실패: {result['message']}")
            
    except Exception as e:
        print(f"🔥 에러 발생: {e}")

if __name__ == "__main__":
    main()