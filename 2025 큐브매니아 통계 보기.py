import pandas as pd
import os

# 1. 파일 경로 설정
file_path = r"C:\Users\Administrator\Desktop\네이버카페\큐브매니아_2025_순수데이터.xlsx"

if not os.path.exists(file_path):
    print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
else:
    df = pd.read_excel(file_path)
    df['조회수'] = pd.to_numeric(df['조회수'], errors='coerce').fillna(0)
    df['제목'] = df['제목'].astype(str)

    print("\n==========================================")
    print("   🎓 2025 큐브매니아 개인 성적표 발급기")
    print("==========================================\n")

    # 전체 통계 미리 계산
    percentiles = [0.04, 0.11, 0.23, 0.40, 0.60, 0.77, 0.89, 0.96, 1.00]
    grade_cuts = df['조회수'].quantile([1-p for p in percentiles]).values
    cafe_top_20 = df.sort_values(by='조회수', ascending=False).head(20)[['제목', '작성자', '조회수', '작성날짜']]

    writer_stats = df.groupby('작성자')['조회수'].agg(['mean', 'max', 'count', 'sum']).reset_index()
    writer_stats.columns = ['작성자', '평균조회수', '최고조회수', '총게시글수', '누적조회수']
    writer_stats['화력순위'] = writer_stats['평균조회수'].rank(ascending=False, method='min')

    while True:
        search_nickname = input("성적표를 출력할 닉네임을 입력하세요 (종료하려면 'q' 입력): ")
        
        if search_nickname.lower() == 'q':
            print("프로그램을 종료합니다. 고생하셨습니다!")
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
            
            # 등급 멘트
            if grade == 1: comment = "🎉 전설적인 활동! 당신은 큐브매니아의 심장입니다. (상위 4%)"
            elif grade <= 3: comment = "⭐ 대단한 영향력! 카페의 핵심 멤버이시군요!"
            elif grade <= 5: comment = "👍 준수한 활동! 2026년에는 1등급을 노려봐요!"
            else: comment = "🌱 2025년 고생하셨습니다. 올해는 더 활발한 활동 기대할게요!"

            # 내 글 TOP 20
            my_top_20 = user_data.sort_values(by='조회수', ascending=False).head(20)[['제목', '작성날짜', '조회수']]
            
            # 요약 보고서 데이터
            report = pd.DataFrame({
                '항목': ['닉네임', '종합 등급', '평가', '2025 총 게시글', '누적 조회수', '평균 조회수(화력)', '내 최고 조회수', '평균 화력 순위'],
                '데이터': [
                    search_nickname, 
                    f"{grade}등급", 
                    comment, 
                    f"{int(user_info['총게시글수'])}개", 
                    f"{int(user_info['누적조회수'])}회", 
                    f"{user_info['평균조회수']:.1f}회", 
                    f"{int(user_info['최고조회수'])}회", 
                    f"전체 {int(user_info['화력순위'])}위"
                ]
            })
            
            output_path = f"C:\\Users\\Administrator\\Desktop\\네이버카페\\2025_성적표_{search_nickname}.xlsx"
            
            # [수정 완료] 오타 수정: to_ -> to_excel
            with pd.ExcelWriter(output_path) as writer:
                report.to_excel(writer, sheet_name='나의_2025_성적표', index=False)
                my_top_20.to_excel(writer, sheet_name='나의_인기글_TOP20', index=False)
                cafe_top_20.to_excel(writer, sheet_name='카페_전체_TOP20', index=False)
                pd.DataFrame({'등급': [f"{i+1}등급" for i in range(9)], '조회수컷': [int(c) for c in grade_cuts]}).to_excel(writer, sheet_name='등급컷_기준표', index=False)

            print(f"✅ {search_nickname}님의 정밀 분석 성적표 생성이 완료되었습니다!")
        else:
            print(f"❌ '{search_nickname}' 닉네임을 찾을 수 없습니다.")