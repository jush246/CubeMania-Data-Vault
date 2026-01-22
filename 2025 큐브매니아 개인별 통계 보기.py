import pandas as pd
import os
import sys

# [추가된 부분] 프로그램 내부(몸체)에 숨겨진 엑셀 파일을 찾는 함수
def resource_path(relative_path):
    try:
        # PyInstaller에 의해 생성된 임시 폴더 경로를 찾음
        base_path = sys._MEIPASS
    except Exception:
        # 일반 파이썬 실행 환경일 때는 현재 폴더 경로를 사용
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 1. 파일 경로 설정 (resource_path 함수를 사용해서 엑셀을 찾음)
file_name = "큐브매니아_2025_순수데이터.xlsx"
file_path = resource_path(file_name)

# 2. 결과 저장 위치 설정 (사용자의 바탕화면)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

def run_report():
    print("\n==========================================")
    print("   🎓 2025 큐브매니아 통합 성적표 발급기")
    print("==========================================\n")

    if not os.path.exists(file_path):
        print(f"❌ 데이터를 찾을 수 없습니다: {file_name}")
        input("엔터 키를 누르면 종료됩니다...")
        return

    # 데이터 로딩
    df = pd.read_excel(file_path)
    df['조회수'] = pd.to_numeric(df['조회수'], errors='coerce').fillna(0)
    df['제목'] = df['제목'].astype(str)

    # 전체 통계 계산 (등급 컷 등)
    percentiles = [0.04, 0.11, 0.23, 0.40, 0.60, 0.77, 0.89, 0.96, 1.00]
    grade_cuts = df['조회수'].quantile([1-p for p in percentiles]).values
    cafe_top_20 = df.sort_values(by='조회수', ascending=False).head(20)[['제목', '작성자', '조회수', '작성날짜']]

    writer_stats = df.groupby('작성자')['조회수'].agg(['mean', 'max', 'count', 'sum']).reset_index()
    writer_stats.columns = ['작성자', '평균조회수', '최고조회수', '총게시글수', '누적조회수']
    writer_stats['화력순위'] = writer_stats['평균조회수'].rank(ascending=False, method='min')

    while True:
        search_nickname = input("성적표를 출력할 닉네임을 입력하세요 (종료하려면 'q' 입력): ")
        
        if search_nickname.lower() == 'q':
            break
            
        user_data = df[df['작성자'] == search_nickname]
        
        if not user_data.empty:
            user_info = writer_stats[writer_stats['작성자'] == search_nickname].iloc[0]
            
            # 등급 판정
            grade = 9
            for i, cut in enumerate(grade_cuts):
                if user_info['최고조회수'] >= cut:
                    grade = i + 1
                    break
            
            # 멘트 설정
            if grade == 1: comment = "🎉 전설적인 활동! 당신은 큐브매니아의 심장입니다."
            elif grade <= 3: comment = "⭐ 대단한 영향력! 카페의 핵심 멤버이시군요!"
            elif grade <= 5: comment = "👍 준수한 활동! 2026년에도 1등급을 노려봐요!"
            else: comment = "🌱 2025년 고생하셨습니다. 올해는 더 활발한 활동 기대할게요!"

            # 개인 데이터 정리
            my_top_20 = user_data.sort_values(by='조회수', ascending=False).head(20)[['제목', '작성날짜', '조회수']]
            report = pd.DataFrame({
                '항목': ['닉네임', '종합 등급', '평가', '총 게시글', '누적 조회수', '평균 조회수', '최고 조회수', '화력 순위'],
                '데이터': [search_nickname, f"{grade}등급", comment, f"{int(user_info['총게시글수'])}개", 
                          f"{int(user_info['누적조회수'])}회", f"{user_info['평균조회수']:.1f}회", 
                          f"{int(user_info['최고조회수'])}회", f"전체 {int(user_info['화력순위'])}위"]
            })
            
            # 바탕화면에 저장
            output_path = os.path.join(desktop_path, f"2025_성적표_{search_nickname}.xlsx")
            with pd.ExcelWriter(output_path) as writer:
                report.to_excel(writer, sheet_name='나의_2025_성적표', index=False)
                my_top_20.to_excel(writer, sheet_name='나의_인기글_TOP20', index=False)
                cafe_top_20.to_excel(writer, sheet_name='카페_전체_TOP20', index=False)
            
            print(f"✅ {search_nickname}님의 성적표가 바탕화면에 생성되었습니다!")
        else:
            print(f"❌ '{search_nickname}' 닉네임을 찾을 수 없습니다.")

if __name__ == "__main__":
    run_report()