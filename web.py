import streamlit as st
import pandas as pd
import os
import io

# 페이지 설정
st.set_page_config(
    page_title="2025 큐브매니아 통합 성적표",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS로 프리미엄 디자인 적용
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border-color: #0056b3;
    }
    .report-card {
        padding: 2rem;
        border-radius: 15px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        text-align: center;
        margin-top: 1rem;
    }
    .metric-box {
        padding: 1rem;
        background: #f1f3f5;
        border-radius: 10px;
        min-width: 120px;
    }
    h1, h2, h3 {
        color: #343a40;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로딩 함수 (캐싱 적용)
@st.cache_data
def load_data(file_name):
    if not os.path.exists(file_name):
        return None
    df = pd.read_excel(file_name)
    df['조회수'] = pd.to_numeric(df['조회수'], errors='coerce').fillna(0)
    df['제목'] = df['제목'].astype(str)
    return df

# 파일명 설정
file_name = "큐브매니아_2025_순수데이터.xlsx"
df = load_data(file_name)

# 사이드바 구성
st.sidebar.title("🎓 큐브매니아 2025")
st.sidebar.info("2025년 카페 활동 통합 성적표를 확인하세요.")

if df is None:
    st.error(f"❌ '{file_name}' 파일을 찾을 수 없습니다. 데이터 수집을 먼저 진행해주세요.")
else:
    # 메인 헤더
    st.title("🏆 2025 큐브매니아 통합 성적표 발급기")
    st.markdown("---")

    # 검색 영역
    col1, col2 = st.columns([3, 1])
    with col1:
        search_nickname = st.text_input("닉네임을 입력하세요", placeholder="예: 큐브매니아")
    with col2:
        st.write("##") # 간격 조절
        search_button = st.button("성적표 발급")

    if search_button or search_nickname:
        user_data = df[df['작성자'] == search_nickname]

        if not user_data.empty:
            # 전체 통계 계산 (등급 컷 등)
            percentiles = [0.04, 0.11, 0.23, 0.40, 0.60, 0.77, 0.89, 0.96, 1.00]
            grade_cuts = df['조회수'].quantile([1-p for p in percentiles]).values
            
            writer_stats = df.groupby('작성자')['조회수'].agg(['mean', 'max', 'count', 'sum']).reset_index()
            writer_stats.columns = ['작성자', '평균조회수', '최고조회수', '총게시글수', '누적조회수']
            writer_stats['화력순위'] = writer_stats['평균조회수'].rank(ascending=False, method='min')
            
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

            # UI 출력 시작
            st.success(f"✅ {search_nickname}님의 성적표가 준비되었습니다!")
            
            # 대시보드 형태의 리포트
            with st.container():
                st.markdown(f"""
                <div class="report-card">
                    <h2 style='text-align: center; color: #007bff;'>[{search_nickname}] 님의 2025 성적표</h2>
                    <h3 style='text-align: center;'>등급: {grade}등급</h3>
                    <p style='text-align: center; font-size: 1.2rem; color: #6c757d;'>{comment}</p>
                    <div class="metric-container">
                        <div class="metric-box">
                            <small>총 게시글</small><br><strong>{int(user_info['총게시글수'])}개</strong>
                        </div>
                        <div class="metric-box">
                            <small>누적 조회수</small><br><strong>{int(user_info['누적조회수']):,}회</strong>
                        </div>
                        <div class="metric-box">
                            <small>평균 조회수</small><br><strong>{user_info['평균조회수']:.1f}회</strong>
                        </div>
                        <div class="metric-box">
                            <small>화력 순위</small><br><strong>전체 {int(user_info['화력순위'])}위</strong>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 탭 구성
            tab1, tab2, tab3 = st.tabs(["📊 나의 인기글 TOP 20", "🔥 카페 전체 TOP 20", "📥 엑셀 다운로드"])
            
            with tab1:
                my_top_20 = user_data.sort_values(by='조회수', ascending=False).head(20)[['제목', '작성날짜', '조회수']]
                st.table(my_top_20)

            with tab2:
                cafe_top_20 = df.sort_values(by='조회수', ascending=False).head(20)[['제목', '작성자', '조회수', '작성날짜']]
                st.table(cafe_top_20)

            with tab3:
                st.info("성적표를 엑셀 파일로 소장하실 수 있습니다.")
                
                # 엑셀 파일 생성 (메모리 버퍼 사용)
                report_df = pd.DataFrame({
                    '항목': ['닉네임', '종합 등급', '평가', '총 게시글', '누적 조회수', '평균 조회수', '최고 조회수', '화력 순위'],
                    '데이터': [search_nickname, f"{grade}등급", comment, f"{int(user_info['총게시글수'])}개", 
                              f"{int(user_info['누적조회수'])}회", f"{user_info['평균조회수']:.1f}회", 
                              f"{int(user_info['최고조회수'])}회", f"전체 {int(user_info['화력순위'])}위"]
                })

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as excel_writer:
                    report_df.to_excel(excel_writer, sheet_name='나의_2025_성적표', index=False)
                    my_top_20.to_excel(excel_writer, sheet_name='나의_인기글_TOP20', index=False)
                    cafe_top_20.to_excel(excel_writer, sheet_name='카페_전체_TOP20', index=False)
                
                excel_data = output.getvalue()
                
                st.download_button(
                    label="💾 엑셀 성적표 다운로드",
                    data=excel_data,
                    file_name=f"2025_성적표_{search_nickname}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            if search_nickname:
                st.error(f"❌ '{search_nickname}' 닉네임을 찾을 수 없습니다.")

    # 하단 정보
    st.markdown("---")
    st.caption("© 2025 CubeMania Data Vault - Powered by Streamlit")
