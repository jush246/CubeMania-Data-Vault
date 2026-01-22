import streamlit as st
import pandas as pd
import os
import io

# 1. 페이지 설정 (탭 이름과 아이콘 변경)
st.set_page_config(
    page_title="CubeMania 2025 Vault",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. 커스텀 CSS (더 현대적이고 세련된 스타일)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main {
        background-color: #0e1117;
    }
    
    /* 성적표 카드 스타일 */
    .report-card {
        padding: 30px;
        border-radius: 20px;
        background: linear-gradient(135deg, #1e2130 0%, #0e1117 100%);
        border: 1px solid #3e4451;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        margin-bottom: 25px;
        color: white;
    }
    
    /* 등급 폰트 강조 */
    .grade-text {
        font-size: 3rem;
        font-weight: 900;
        background: -webkit-linear-gradient(#ffd700, #ff8c00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }

    /* 메트릭 박스 디자인 */
    .metric-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-box:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        border-radius: 8px;
        background: linear-gradient(90deg, #007bff, #00d4ff);
        border: none;
        color: white;
        transition: all 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로딩 함수 (기존과 동일)
@st.cache_data
def load_data(file_name):
    if not os.path.exists(file_name):
        return None
    df = pd.read_excel(file_name)
    df['조회수'] = pd.to_numeric(df['조회수'], errors='coerce').fillna(0)
    df['제목'] = df['제목'].astype(str)
    return df

file_name = "큐브매니아_2025_순수데이터.xlsx"
df = load_data(file_name)

# 사이드바
st.sidebar.image("https://img.icons8.com/fluency/96/cube.png", width=80)
st.sidebar.title("CubeMania Vault")
st.sidebar.markdown("---")
st.sidebar.write("📅 **2025년 통합 성적표**")
st.sidebar.info("당신의 열정을 데이터로 확인하세요.")

if df is None:
    st.error(f"❌ '{file_name}' 파일을 찾을 수 없습니다.")
else:
    # 헤더 섹션
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🏆 2025 성적표 발급기</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>큐브매니아 카페 활동 데이터를 기반으로 산출된 공식 리포트입니다.</p>", unsafe_allow_html=True)
    
    # 검색창을 중앙으로 배치하기 위한 컬럼 설정
    _, search_col, _ = st.columns([1, 2, 1])
    with search_col:
        search_nickname = st.text_input("", placeholder="닉네임을 입력하고 엔터를 누르세요")
    
    if search_nickname:
        user_data = df[df['작성자'] == search_nickname]

        if not user_data.empty:
            # 데이터 계산 부분 (기존 로직 유지)
            percentiles = [0.04, 0.11, 0.23, 0.40, 0.60, 0.77, 0.89, 0.96, 1.00]
            grade_cuts = df['조회수'].quantile([1-p for p in percentiles]).values
            writer_stats = df.groupby('작성자')['조회수'].agg(['mean', 'max', 'count', 'sum']).reset_index()
            writer_stats.columns = ['작성자', '평균조회수', '최고조회수', '총게시글수', '누적조회수']
            writer_stats['화력순위'] = writer_stats['평균조회수'].rank(ascending=False, method='min')
            user_info = writer_stats[writer_stats['작성자'] == search_nickname].iloc[0]

            grade = 9
            for i, cut in enumerate(grade_cuts):
                if user_info['최고조회수'] >= cut:
                    grade = i + 1
                    break

            # 성적표 카드 출력
            st.markdown(f"""
                <div class="report-card">
                    <p style='text-align: center; font-size: 1.5rem; margin-bottom: 0;'>2025 OFFICIAL REPORT</p>
                    <h1 style='text-align: center; margin-top: 0;'>{search_nickname}</h1>
                    <div class="grade-text">{grade}등급</div>
                    <p style='text-align: center; font-size: 1.1rem; color: #aaa;'>상위 {int(percentiles[grade-1]*100)}% 이내의 활약</p>
                </div>
            """, unsafe_allow_html=True)

            # 지표 4개를 가로로 예쁘게
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("총 게시글", f"{int(user_info['총게시글수'])}개")
            m2.metric("누적 조회수", f"{int(user_info['누적조회수']):,}회")
            m3.metric("평균 조회수", f"{user_info['평균조회수']:.1f}회")
            m4.metric("화력 순위", f"전체 {int(user_info['화력순위'])}위")

            st.markdown("<br>", unsafe_allow_html=True)

            # 탭 디자인
            tab1, tab2, tab