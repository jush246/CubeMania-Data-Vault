# 등급 판정 및 백분위 계산 로직 (기존과 동일)
            grade = 9
            for i, cut in enumerate(grade_cuts):
                if user_info['최고조회수'] >= cut:
                    grade = i + 1
                    break
            
            # 실제 화력 백분위 계산
            raw_pct = (writer_stats['평균조회수'].rank(pct=True).loc[user_info.name])
            user_pct_val = (1 - raw_pct) * 100

            # [수정된 부분] 성적표 카드 출력 (구간 설명 제거, 실제 백분위 강조)
            st.markdown(f"""
                <div class="report-card">
                    <p style='text-align: center; font-size: 1.2rem; color: #888; margin-bottom: 0;'>2025 OFFICIAL REPORT</p>
                    <h1 style='text-align: center; margin-top: 0;'>{search_nickname}</h1>
                    <div class="grade-text">{grade}등급</div>
                    <p style='text-align: center; font-size: 1.3rem; font-weight: bold; color: #ffd700;'>
                        실제 화력 백분위: 상위 {user_pct_val:.1f}%
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # 지표 레이아웃
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("총 게시글", f"{int(user_info['총게시글수'])}개")
            m2.metric("누적 조회수", f"{int(user_info['누적조회수']):,}회")
            m3.metric("평균 조회수", f"{user_info['평균조회수']:.1f}회")
            m4.metric("화력 순위", f"전체 {int(user_info['화력순위'])}위")
            
            # [추가된 부분] 등급 및 화력 설명 섹션
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                with st.expander("🎓 등급은 어떻게 결정되나요?"):
                    st.write("""
                        **최고 조회수**를 기준으로 결정됩니다. 
                        - 1등급: 상위 4%
                        - 2등급: 상위 11%
                        - 3등급: 상위 23%
                        - ... (이후 40%, 60%, 77%, 89%, 96%, 100% 기준)
                        한 번이라도 큰 파급력을 보여준 게시글이 있다면 높은 등급을 받게 됩니다.
                    """)
            with col_exp2:
                with st.expander("🔥 화력 순위 및 백분위 기준"):
                    st.write("""
                        **평균 조회수**를 기준으로 합니다. 
                        단순히 글을 많이 쓴 것이 아니라, 게시글 하나당 얼마나 많은 사람들의 반응을 이끌어냈는지를 나타내는 '평균 파급력' 지표입니다. 
                        백분위가 0%에 가까울수록 카페 내 영향력이 높음을 의미합니다.
                    """)

            st.markdown("<br>", unsafe_allow_html=True)