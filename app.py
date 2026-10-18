                        ),
                        "지연시간(ms)": float(
                            data["delay"]
                        )
                    })

                # 정답률 높은 순 → 오답 적은 순 → 2단계 반응시간 빠른 순
                ranking_data.sort(
                    key=lambda x: (
                        -x["정답률(%)"],
                        x["오답 횟수"],
                        x["2단계 평균(ms)"]
                    )
                )

                if ranking_data:
                    for i, item in enumerate(
                        ranking_data, start=1
                    ):
                        item["순위"] = i

                    columns = [
                        "순위",
                        "닉네임",
                        "정답률(%)",
                        "오답 횟수",
                        "2단계 평균(ms)",
                        "1단계 평균(ms)",
                        "지연시간(ms)"
                    ]

                    st.dataframe(
                        [
                            {col: item[col] for col in columns}
                            for item in ranking_data
                        ],
                        use_container_width=True,
                        hide_index=True
                    )

                    st.caption(
                        "순위 기준: 정답률 높은 순 → "
                        "오답 횟수 적은 순 → "
                        "2단계 평균 반응시간 빠른 순"
                    )

                else:
                    st.info("아직 저장된 실험 기록이 없습니다.")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button(
                        "🔄 랭킹 새로고침",
                        use_container_width=True
                    ):
                        st.rerun()

                with col2:
                    if st.button(
                        "랭킹 닫기",
                        use_container_width=True
                    ):
                        st.session_state.ranking_view = False
                        st.rerun()

            except Exception as e:
                st.error(f"랭킹 조회 실패: {e}")


# =========================================================
# 7. 1단계 안내
# =========================================================

elif st.session_state.stage == "1단계안내":

    st.success("🟢 1단계 통제 실험")

    st.markdown("### 📢 1단계 규칙")

    st.write("화살표가 화면 정가운데에 나타납니다.")

    st.info(
        "← 이면 LEFT, → 이면 RIGHT 버튼을 누르세요."
    )

    st.write(
        "화살표 방향에 맞는 버튼을 최대한 빠르게 누르세요."
    )

    if st.button(
        "🚀 1단계 시작하기",
        use_container_width=True
    ):
        run_countdown()

        st.session_state.stage = 1
        st.session_state.trial_count = 0
        st.session_state.feedback = None
        st.session_state.ready = True

        generate_question()

        st.session_state.start_time = time.time()
        st.rerun()


# =========================================================
# 8. 1단계 → 2단계 전환
# =========================================================

elif st.session_state.stage == "전환기":

    st.success("🎉 1단계 통제 실험 완료!")

    st.markdown("### 📢 2단계 인지 간섭 실험")

    st.write(
        "화살표가 화면 왼쪽 또는 오른쪽에 나타납니다."
    )

    st.warning(
        "화살표의 위치를 무시하고 기호의 방향대로 누르세요."
    )

    if st.button(
        "🚀 2단계 시작하기",
        use_container_width=True
    ):
        run_countdown()

        st.session_state.stage = 2
        st.session_state.trial_count = 0
        st.session_state.feedback = None
        st.session_state.ready = True

        generate_question()

        st.session_state.start_time = time.time()
        st.rerun()


# =========================================================
# 9. 실험 진행
# =========================================================

elif st.session_state.stage in [1, 2]:

    if (
        st.session_state.feedback is None
        and st.session_state.start_time == 0.0
        and st.session_state.ready
    ):
        st.session_state.start_time = time.time()

    if st.session_state.stage == 1:
        st.success(
            f"▶ 1단계 진행 중 ({st.session_state.trial_count}/5)"
        )
        st.write("화살표는 정가운데에 나타납니다.")
