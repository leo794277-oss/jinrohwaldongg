# 실행:
# python -m streamlit run c:/Users/User/Desktop/app.py

import streamlit as st
import time
import random
from supabase import create_client, Client


# =========================================================
# 0. Supabase 연결
# =========================================================

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    # 로컬에서 테스트할 경우 여기에 직접 입력
    SUPABASE_URL = "여기에_너의_Supabase_URL"
    SUPABASE_KEY = "여기에_너의_Supabase_anon_key"

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# 1. 페이지 설정
# =========================================================

st.set_page_config(
    page_title="단계별 뇌 인지 실험",
    layout="centered"
)


# =========================================================
# 2. 세션 상태 초기화
# =========================================================

if "stage" not in st.session_state:
    st.session_state.stage = "시작화면"

if "trial_count" not in st.session_state:
    st.session_state.trial_count = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = 0.0

if "current_arrow" not in st.session_state:
    st.session_state.current_arrow = "←"

if "current_pos" not in st.session_state:
    st.session_state.current_pos = "center"

if "results" not in st.session_state:
    st.session_state.results = []

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "ready" not in st.session_state:
    st.session_state.ready = False

if "nickname" not in st.session_state:
    st.session_state.nickname = ""

if "db_saved" not in st.session_state:
    st.session_state.db_saved = False


# =========================================================
# 3. 문제 출제 함수
# =========================================================

def generate_question():

    st.session_state.current_arrow = random.choice([
        "←",
        "→"
    ])

    if st.session_state.stage == 1:

        # 1단계: 가운데 고정
        st.session_state.current_pos = "center"

    elif st.session_state.stage == 2:

        # 2단계: 왼쪽 또는 오른쪽
        st.session_state.current_pos = random.choice([
            "left",
            "right"
        ])


# =========================================================
# 4. 모바일 진동 + 화면 효과
# =========================================================

if st.session_state.feedback == "correct":

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #e2fcd5 !important;
            transition: background-color 0.1s;
        }

        .arrow-box {
            animation: arrow-pop 0.3s ease-in-out;
            display: inline-block;
            width: 100%;
        }

        @keyframes arrow-pop {
            0% {
                transform: scale(1);
            }

            50% {
                transform: scale(1.3);
            }

            100% {
                transform: scale(1);
            }
        }
        </style>

        <script>
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }
        </script>
        """,
        unsafe_allow_html=True
    )

elif st.session_state.feedback == "wrong":

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #fce2e2 !important;
            transition: background-color 0.1s;
        }

        .arrow-box {
            animation: arrow-pop 0.3s ease-in-out;
            display: inline-block;
            width: 100%;
        }

        @keyframes arrow-pop {
            0% {
                transform: scale(1);
            }

            50% {
                transform: scale(1.3);
            }

            100% {
                transform: scale(1);
            }
        }
        </style>

        <script>
        if (navigator.vibrate) {
            navigator.vibrate();
        }
        </script>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f0f2f6 !important;
        }

        .arrow-box {
            display: inline-block;
            width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 5. 카운트다운
# =========================================================

def run_countdown():

    countdown_placeholder = st.empty()

    for i in [3, 2, 1]:

        countdown_placeholder.markdown(
            f"""
            <h1 style="
                text-align: center;
                font-size: 100px;
                color: #ff4b4b;
                margin: 0;
                margin-top: -60px;
            ">
                {i}
            </h1>
            """,
            unsafe_allow_html=True
        )

        time.sleep(1.0)

    countdown_placeholder.markdown(
        """
        <h1 style="
            text-align: center;
            font-size: 100px;
            color: #28a745;
            margin: 0;
            margin-top: -60px;
        ">
            START!
        </h1>
        """,
        unsafe_allow_html=True
    )

    time.sleep(0.6)

    countdown_placeholder.empty()


# =========================================================
# 6. 제목
# =========================================================

st.title("🧠 단계별 인지 간섭 시뮬레이터")


# =========================================================
# 7. 시작 화면
# =========================================================

if st.session_state.stage == "시작화면":

    st.info(
        "👋 안녕하세요! 뇌 인지 간섭 실험 사이트에 오신 것을 환영합니다."
    )

    nickname = st.text_input(
        "닉네임을 입력하세요",
        max_chars=20
    )

    st.write(
        "본 실험은 스마트폰 모바일 터치 환경에 최적화되어 있습니다."
    )

    st.write(
        "정밀한 측정을 위해 **[스마트폰 진동 및 소리]**를 켜주시고 "
        "진지하게 임해 주세요!"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "🚀 실험 홈 진입하기",
        use_container_width=True
    ):

        if nickname.strip():

            st.session_state.nickname = nickname.strip()
            st.session_state.stage = "1단계안내"
            st.session_state.db_saved = False

            st.rerun()

        else:

            st.warning("닉네임을 입력해주세요.")


# =========================================================
# 8. 1단계 안내
# =========================================================

elif st.session_state.stage == "1단계안내":

    st.success(
        "🟢 먼저 [ 1단계 통제 실험 ] 을 진행합니다."
    )

    st.markdown("### 📢 1단계 규칙 설명")

    st.write(
        "1단계에서는 화살표 기호가 무조건 화면 "
        "**정가운데 고정**된 상태로 나타납니다."
    )

    st.info(
        "💡 **버튼 규칙**: 화면 하단의 "
        "**[👈 LEFT] 버튼은 왼쪽 화살표(←)**를, "
        "**[👉 RIGHT] 버튼은 오른쪽 화살표(→)**를 의미합니다."
    )

    st.write(
        "화살표 모양이 뜨자마자 방향에 맞는 버튼을 "
        "최대한 빛의 속도로 터치하세요!"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    button_place = st.empty()

    if button_place.button(
        "🚀 1단계 시작하기",
        use_container_width=True
    ):

        button_place.empty()

        run_countdown()

        st.session_state.stage = 1
        st.session_state.ready = True

        generate_question()

        st.session_state.start_time = time.time()

        st.rerun()


# =========================================================
# 9. 1단계 → 2단계 전환 화면
# =========================================================

elif st.session_state.stage == "전환기":

    st.info(
        "🎉 1단계(통제 실험)가 완료되었습니다!"
    )

    st.markdown(
        "### 📢 다음은 2단계(인지 간섭 실험)입니다."
    )

    st.write(
        "2단계부터는 화살표가 화면 "
        "**왼쪽이나 오른쪽** 중 무작위 위치에서 나타납니다."
    )

    st.warning(
        "🔥 **핵심**: 화살표가 나타나는 '위치'는 무조건 무시하고, "
        "오직 **[화살표 기호의 방향]**대로만 아래 버튼을 터치해야 합니다!"
    )

    st.info(
        "💡 **버튼 규칙 동일**: 화살표 모양이 "
        "**←** 이면 [👈 LEFT], "
        "**→** 이면 [👉 RIGHT] 버튼을 누르세요."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    button_place2 = st.empty()

    if button_place2.button(
        "🚀 2단계 시작하기",
        use_container_width=True
    ):

        button_place2.empty()

        run_countdown()

        st.session_state.stage = 2
        st.session_state.ready = True

        generate_question()

        st.session_state.start_time = time.time()

        st.rerun()


# =========================================================
# 10. 1단계 / 2단계 실험
# =========================================================

elif (
    st.session_state.stage == 1
    or st.session_state.stage == 2
):

    # 최초 시작 시간 설정
    if (
        st.session_state.feedback is None
        and st.session_state.start_time == 0.0
        and st.session_state.ready is True
    ):

        st.session_state.start_time = time.time()


    # -----------------------------------------------------
    # 현재 단계 표시
    # -----------------------------------------------------

    if st.session_state.stage == 1:

        st.success(
            f"▶ 현재 [ 1단계 ] 진행 중 "
            f"({st.session_state.trial_count} / 5)"
        )

        st.write(
            "💡 화살표가 **정가운데**에만 나타납니다. "
            "방향대로 빠르게 버튼을 누르세요!"
        )

    else:

        st.warning(
            f"▶ 현재 [ 2단계 ] 진행 중 "
            f"({st.session_state.trial_count} / 5)"
        )

        st.write(
            "🔥 **주의**: 화살표가 **양옆**에 나타납니다. "
            "위치는 무시하고 **[화살표 방향]**대로만 누르세요!"
        )


    st.markdown("<br>", unsafe_allow_html=True)


    # -----------------------------------------------------
    # 피드백
    # -----------------------------------------------------

    if st.session_state.feedback == "correct":

        st.markdown(
            """
            <h3 style="
                text-align: center;
                color: #28a745;
            ">
                🟢 정답입니다! (다음 문제 이동)
            </h3>
            """,
            unsafe_allow_html=True
        )

    elif st.session_state.feedback == "wrong":

        st.markdown(
            """
            <h3 style="
                text-align: center;
                color: #dc3545;
            ">
                🔴 틀렸습니다! (다시 시도하세요)
            </h3>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <h3 style="
                text-align: center;
                color: transparent;
            ">
                대기
            </h3>
            """,
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # 화살표 표시
    # -----------------------------------------------------

    col_l, col_c, col_r = st.columns(3)


    if st.session_state.current_pos == "left":

        with col_l:

            st.markdown(
                f"""
                <div class='arrow-box'
                     style='
                        text-align: center;
                        color: #007bff;
                        font-size: 80px;
                        font-weight: bold;
                     '>
                    {st.session_state.current_arrow}
                </div>
                """,
                unsafe_allow_html=True
            )


    elif st.session_state.current_pos == "right":

        with col_r:

            st.markdown(
                f"""
                <div class='arrow-box'
                     style='
                        text-align: center;
                        color: #007bff;
                        font-size: 80px;
                        font-weight: bold;
                     '>
                    {st.session_state.current_arrow}
                </div>
                """,
                unsafe_allow_html=True
            )


    else:

        with col_c:

            st.markdown(
                f"""
                <div class='arrow-box'
                     style='
                        text-align: center;
                        color: #28a745;
                        font-size: 80px;
                        font-weight: bold;
                     '>
                    {st.session_state.current_arrow}
                </div>
                """,
                unsafe_allow_html=True
            )


    st.markdown("<br><br>", unsafe_allow_html=True)


    # -----------------------------------------------------
    # 버튼
    # -----------------------------------------------------

    btn_col1, btn_col2 = st.columns(2)

    user_choice = None


    with btn_col1:

        if st.button(
            "👈 LEFT (왼쪽)",
            use_container_width=True
        ):

            user_choice = "←"


    with btn_col2:

        if st.button(
            "👉 RIGHT (오른쪽)",
            use_container_width=True
        ):

            user_choice = "→"


    # -----------------------------------------------------
    # 버튼을 눌렀을 때
    # -----------------------------------------------------

    if user_choice is not None:

        end_time = time.time()


        # 아직 답변하지 않은 상태에서만 기록
        if st.session_state.feedback is None:

            reaction_time = (
                end_time - st.session_state.start_time
            ) * 1000


            is_correct = (
                st.session_state.current_arrow
                == user_choice
            )


            # 결과 저장
            st.session_state.results.append(
                {
                    "단계": f"{st.session_state.stage}단계",
                    "반응시간(ms)": round(
                        reaction_time,
                        2
                    ),
                    "정답여부": is_correct
                }
            )


            # 정답
            if is_correct:

                st.session_state.feedback = "correct"

                st.session_state.trial_count += 1


            # 오답
            else:

                st.session_state.feedback = "wrong"


            st.rerun()


    # -----------------------------------------------------
    # 피드백 후 다음 문제
    # -----------------------------------------------------

    if st.session_state.feedback in [
        "correct",
        "wrong"
    ]:

        time.sleep(0.4)


        # -----------------------------
        # 정답
        # -----------------------------

        if st.session_state.feedback == "correct":

            st.session_state.start_time = 0.0


            # 5문제 완료
            if st.session_state.trial_count >= 5:

                # 1단계 완료
                if st.session_state.stage == 1:

                    st.session_state.stage = "전환기"
                    st.session_state.trial_count = 0


                # 2단계 완료
                elif st.session_state.stage == 2:

                    st.session_state.stage = "종료"


            # 아직 5문제 미만
            else:

                generate_question()


        # -----------------------------
        # 오답
        # -----------------------------

        elif st.session_state.feedback == "wrong":

            # 같은 문제 다시 시도
            st.session_state.start_time = time.time()


        st.session_state.feedback = None

        st.rerun()


# =========================================================
# 11. 실험 종료 + 결과
# =========================================================

elif st.session_state.stage == "종료":

    st.balloons()

    st.success(
        "🎉 모든 테스트가 완료되었습니다! "
        "참여해 주셔서 감사합니다."
    )


    # -----------------------------------------------------
    # 단계별 반응시간 추출
    # -----------------------------------------------------

    stage1_times = [
        r["반응시간(ms)"]
        for r in st.session_state.results
        if r["단계"] == "1단계"
    ]


    stage2_times = [
        r["반응시간(ms)"]
        for r in st.session_state.results
        if r["단계"] == "2단계"
    ]


    # -----------------------------------------------------
    # 평균 계산
    # -----------------------------------------------------

    avg_stage1 = (
        round(
            sum(stage1_times) / len(stage1_times),
            2
        )
        if stage1_times
        else 0
    )


    avg_stage2 = (
        round(
            sum(stage2_times) / len(stage2_times),
            2
        )
        if stage2_times
        else 0
    )


    # -----------------------------------------------------
    # 지연시간
    # -----------------------------------------------------

    delay = round(
        avg_stage2 - avg_stage1,
        2
    )


    # =====================================================
    # Supabase 저장
    # =====================================================

    if not st.session_state.db_saved:

        try:

            supabase.table(
                "experiment_results"
            ).insert(
                {
                    "nickname": st.session_state.nickname,
                    "stage1_avg": avg_stage1,
                    "stage2_avg": avg_stage2
                }
            ).execute()


            # 저장 성공
            st.session_state.db_saved = True

            st.success(
                "✅ 실험 결과가 Supabase DB에 저장되었습니다!"
            )


        except Exception as e:

            st.error(
                f"❌ Supabase DB 저장 실패: {e}"
            )


    # -----------------------------------------------------
    # 결과 화면
    # -----------------------------------------------------

    st.markdown(
        "## 📊 인지 속도 결과 분석"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            label="🟢 1단계 평균 속도 (중앙 고정)",
            value=f"{avg_stage1} ms"
        )


    with col2:

        st.metric(
            label="🔵 2단계 평균 속도 (공간 충돌)",
            value=f"{avg_stage2} ms"
        )


    st.markdown(
        f"""
        💡 공간 충돌로 인해 당신의 뇌는
        **평균 {delay} ms 만큼 지연**되었습니다.
        """
    )


    st.markdown("<br><br>", unsafe_allow_html=True)


    # =====================================================
    # 다시 시작
    # =====================================================

    if st.button(
        "🔄 처음부터 다시 도전하기",
        use_container_width=True
    ):

        st.session_state.stage = "시작화면"

        st.session_state.trial_count = 0

        st.session_state.start_time = 0.0

        st.session_state.results = []

        st.session_state.feedback = None

        st.session_state.ready = False

        st.session_state.nickname = ""

        st.session_state.db_saved = False

        st.rerun()
