import streamlit as st
import pandas as pd
import os
import io

# 1. 페이지 설정
st.set_page_config(
    page_title="CubeMania 2025 Vault",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. 커스텀 CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    .main { background-color: #0e1117; }
    .report-card {
        padding: 30px;
        border-radius: 20px;
        background: linear-gradient(135deg, #1e2130 0%, #0e1117 100%);
        border: 1px solid #3e4451;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
        color: white;
    }
    .grade-text {
        font-size: 3.5rem;
        font-weight: 900;
        background: -webkit-linear-gradient(#ffd700, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 10px 0;
    }
    .stButton>button {
        border-radius: 8px;
        background: linear-gradient(90deg, #007bff, #00d4ff);
        border: none;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 데이터 로딩
@st.cache_data
def load_data(file_name):
    if not os.path.exists(file_name): return None
    df = pd.read_excel(file_name)
    df['조회수'] = pd.to_numeric(df['조회수'], errors='coerce').fillna(0)
    df['제목'] = df['제목'].astype(str)
    return df

file_name = "큐브매니아_2025_순수데이터.xlsx"
df = load_data(file_name)

# 4. 사이드바
st.sidebar.image("https://img.icons8.com/fluency/96/cube.png", width=80)
st.sidebar.title("CubeMania Vault")
st.sidebar.info("2025-2026 활동 데이터 분석")

if df is None:
    st.error(f"❌ '{file_name}' 파일을 찾을 수 없습니다.")
else:
    st.markdown("<h1 style='text-align: center;'>🏆 2025 성적표 발급기</h1>", unsafe_allow_html=True)
    
    _, search_col, _ = st.columns([1, 2, 1])
    with search_col:
        search_nickname = st.text_input("", placeholder="닉네임을 입력하고 엔터를 누르세요")
    
    if search_nickname:
        user_data = df[df['작성자'] == search_nickname]

        if not user_data.empty:
            # --- 통계 계산 ---
            percentiles = [0.04, 0.11, 0.23, 0.40, 0.60, 0.77, 0.89, 0.96, 1.00]
            grade_cuts = df['조회수'].quantile([1-p for p in percentiles]).values
            
            writer_stats = df.groupby('작성자')['조회수'].agg(['mean', 'max', 'count', 'sum']).reset_index()
            writer_stats.columns = ['작성자', '평균조회수', '최고조회수', '총게시글수', '누적조회수']
            writer_stats['화력순위'] = writer_stats['평균조회수'].rank(ascending=False, method='min')
            
            user_info = writer_stats[writer_stats['작성자'] == search_nickname].iloc[0]
            
            # 1. 최고 조회수 백분위 (전체 게시글 중 위치)
            top_view_pct = (df['조회수'] > user_info['최고조회수']).mean() * 100
            
            # 2. 실제 화력 백분위 (전체 작성자 중 위치)
            raw_pct = (writer_stats['평균조회수'].rank(pct=True).loc[user_info.name])
            user_pct_val = (1 - raw_pct) * 100

            # 3. 등급 판정
            grade = 9
            for i, cut in enumerate(grade_cuts):
                if user_info['최고조회수'] >= cut:
                    grade = i + 1
                    break

            # --- UI 출력 ---
            # 성적표 카드
            st.markdown(f"""
                <div class="report-card">
                    <p style='text-align: center; font-size: 1.2rem; color: #888; margin-bottom: 0;'>OFFICIAL ANALYSIS</p>
                    <h1 style='text-align: center; margin-top: 0;'>{search_nickname}</h1>
                    <div class="grade-text">{grade}등급</div>
                    <p style='text-align: center; font-size: 1.1rem; margin-bottom: 5px;'>
                        최고 조회수 기록: <span style='color: #00d4ff; font-weight: bold;'>상위 {top_view_pct:.2f}%</span>
                    </p>
                    <p style='text-align: center; font-size: 1.3rem; font-weight: bold; color: #ffd700;'>
                        실제 화력 백분위: 상위 {user_pct_val:.1f}%
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # 지표 메트릭
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("총 게시글", f"{int(user_info['총게시글수'])}개")
            m2.metric("누적 조회수", f"{int(user_info['누적조회수']):,}회")
            m3.metric("평균 조회수", f"{user_info['평균조회수']:.1f}회")
            m4.metric("화력 순위", f"전체 {int(user_info['화력순위'])}위")
            
            # 설명 섹션
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                with st.expander("🎓 등급은 어떻게 결정되나요?"):
                    st.write("최고 조회수를 기준으로 결정됩니다. '상위 4%' 안에 드는 글이 하나라도 있으면 1등급을 획득합니다.")
            with col_exp2:
                with st.expander("🔥 화력 순위 및 백분위 기준"):
                    st.write("평균 조회수를 기준으로 한 '인플루언서' 지표입니다. 백분위가 낮을수록 모든 글이 골고루 인기가 많음을 뜻합니다.")

            st.markdown("<br>", unsafe_allow_html=True)

            # 탭 섹션
            tab1, tab2, tab3 = st.tabs(["📊 나의 인기글 TOP 100", "🏆 전체 랭킹 TOP 100", "📥 데이터 소장"])
            
            with tab1:
                my_top = user_data.sort_values(by='조회수', ascending=False).head(100)[['제목', '작성날짜', '조회수']]
                st.dataframe(my_top, use_container_width=True)

            with tab2:
                cafe_top = df.sort_values(by='조회수', ascending=False).head(100)[['제목', '작성자', '조회수']]
                def highlight_me(row):
                    if row['작성자'] == search_nickname:
                        return ['background-color: #007bff; color: white'] * len(row)
                    return [''] * len(row)
                st.dataframe(cafe_top.style.apply(highlight_me, axis=1), use_container_width=True)

            with tab3:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    user_data.to_excel(writer, index=False)
                st.download_button("💾 엑셀 다운로드", output.getvalue(), f"Report_{search_nickname}.xlsx")

        else:
            st.warning("등록된 닉네임이 없습니다! 정확한 닉네임을 입력해 주세요.")

    st.markdown("<br><br><p style='text-align: center; color: #555;'>CubeMania Data Vault v2.7 | © 2026</p>", unsafe_allow_html=True)