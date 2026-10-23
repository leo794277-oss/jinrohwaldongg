import streamlit as st
import time
import random
import firebase_admin
from firebase_admin import credentials, firestore

# =========================================================
# 0. 페이지 설정 및 Firebase 연결
# =========================================================

st.set_page_config(
    page_title="단계별 뇌 인지 실험",
    layout="centered"
)


@st.cache_resource
def get_firestore_client():
    if not firebase_admin._apps:
        service_account_info = dict(
            st.secrets["firebase_service_account"]
        )

        if "private_key" in service_account_info:
            service_account_info["private_key"] = (
                service_account_info["private_key"].replace(
                    "\\n", "\n"
                )
            )

        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)

    return firestore.client()


try:
    db = get_firestore_client()
    firebase_error = None
except Exception as e:
    db = None
    firebase_error = str(e)


# =========================================================
# 1. 세션 상태 초기화
# =========================================================

defaults = {
    "stage": "시작화면",
    "trial_count": 0,
    "start_time": 0.0,
    "current_arrow": "←",
    "current_pos": "center",
    "results": [],
    "feedback": None,
    "ready": False,
    "nickname": "",
    "db_saved": False,
    "ranking_view": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 데이터 신뢰도를 확보하기 위해 문항 수를 10회로 지정합니다.
TOTAL_TRIALS = 10

# =========================================================
# 2. 문제 출제
# =========================================================

def generate_question():
    st.session_state.current_arrow = random.choice([
        "←", "→"
    ])

    if st.session_state.stage == 1:
        st.session_state.current_pos = "center"

    elif st.session_state.stage == 2:
        st.session_state.current_pos = random.choice([
            "left", "right"
        ])


# =========================================================
# 3. 화면 효과 및 닉네임 입력창 스타일
# =========================================================

if st.session_state.feedback == "correct":
    bg_color = "#e2fcd5"
elif st.session_state.feedback == "wrong":
    bg_color = "#fce2e2"
else:
    bg_color = "#f0f2f6"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color} !important;
        transition: background-color 0.1s;
    }}

    .arrow-box {{
        display: inline-block;
        width: 100%;
        animation: arrow-pop 0.3s ease-in-out;
    }}

    @keyframes arrow-pop {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.3); }}
        100% {{ transform: scale(1); }}
    }}

    /* 닉네임 입력창 */
    div[data-testid="stTextInput"] input {{
        background-color: #ffffff !important;
        color: #222222 !important;
        border: 2px solid #4A90E2 !important;
        border-radius: 10px !important;
        min-height: 52px !important;
        font-size: 18px !important;
        padding: 10px 14px !important;
    }}

    /* 입력창 라벨 */
    div[data-testid="stTextInput"] label {{
        color: #222222 !important;
        font-size: 17px !important;
        font-weight: 700 !important;
    }}

    /* 입력창 안내 문구 */
    div[data-testid="stTextInput"] input::placeholder {{
        color: #777777 !important;
        opacity: 1 !important;
    }}

    /* 입력창 선택 시 */
    div[data-testid="stTextInput"] input:focus {{
        border-color: #1D65C1 !important;
        box-shadow: 0 0 0 2px rgba(29, 101, 193, 0.2) !important;
    }}

     /* 모바일에서도 선택지를 좌우로 배치 */
    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: nowrap !important;
    }}

    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
        min-width: 0 !important;
        flex: 1 1 0% !important;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 4. 카운트다운
# =========================================================

def run_countdown():
    placeholder = st.empty()

    for i in[3,2,1]:
        placeholder.markdown(
            f"""
            <h1 style="
                text-align:center;
                font-size:100px;
                color:#ff4b4b;
            ">{i}</h1>
            """,
            unsafe_allow_html=True
        )
        time.sleep(1)

    placeholder.markdown(
        """
        <h1 style="
            text-align:center;
            font-size:100px;
            color:#28a745;
        ">START!</h1>
        """,
        unsafe_allow_html=True
    )

    time.sleep(0.6)
    placeholder.empty()


# =========================================================
# 5. 제목 및 사이드바
# =========================================================

st.title("🧠 단계별 인지 간섭 시뮬레이터")

if db is not None:
    st.sidebar.success("Firebase 연결 성공")
else:
    st.sidebar.error(f"Firebase 연결 실패: {firebase_error}")


# =========================================================
# 6. 시작 화면 + 랭킹
# =========================================================

if st.session_state.stage == "시작화면":

    st.info(
        "👋 뇌 인지 간섭 실험 사이트에 오신 것을 환영합니다."
    )

    # 닉네임 입력창
    nickname = st.text_input(
        "닉네임을 입력하세요",
        placeholder="여기에 닉네임을 입력하세요",
        max_chars=20,
        key="nickname_input"
    )

    st.write(
        "본 실험은 스마트폰 모바일 터치 환경에 최적화되어 있습니다."
    )

    st.write(
        "정밀한 측정을 위해 스마트폰 진동 및 소리를 켜주세요."
    )

    if st.button(
        "🚀 실험 홈 진입하기",
        use_container_width=True
    ):
        clean_nickname = nickname.strip()

        if not clean_nickname:
            st.warning("닉네임을 입력해주세요.")

        else:
            st.session_state.nickname = clean_nickname
            st.session_state.stage = "1단계안내"
            st.session_state.db_saved = False
            st.session_state.results = []
            st.session_state.trial_count = 0
            st.session_state.feedback = None
            st.session_state.ready = False
            st.rerun()


   
    # -----------------------------
    # 랭킹 영역
    # -----------------------------

    st.markdown("---")
    st.subheader("🏆 실험 랭킹")

    if st.button(
        "🏆 랭킹 보기",
        use_container_width=True
    ):
        st.session_state.ranking_view = True

    if st.session_state.ranking_view:

        if db is None:
            st.error("Firebase에 연결되지 않았습니다.")

        else:
            try:
                docs = db.collection(
                    "experiment_results"
                ).stream()

                ranking_data = []

                for doc in docs:
                    data = doc.to_dict() or {}

                    if (
                        "nickname" not in data
                        or "stage1_avg" not in data
                        or "stage2_avg" not in data
                    ):
                        continue

                    stage1_avg = float(data["stage1_avg"])
                    stage2_avg = float(data["stage2_avg"])

                    ranking_data.append({
                        "닉네임": data["nickname"],
                        "1단계 평균(ms)": stage1_avg,
                        "2단계 평균(ms)": stage2_avg,
                        "평균 반응시간 합(ms)": round(
                            stage1_avg + stage2_avg, 2
                        )
                    })

                # 두 단계 평균 반응시간 합이 작은 순
                ranking_data.sort(
                    key=lambda x: x["평균 반응시간 합(ms)"]
                )

                if ranking_data:
                    for i, item in enumerate(
                        ranking_data, start=1
                    ):
                        item["순위"] = i

                    columns = [
                        "순위",
                        "닉네임",
                        "1단계 평균(ms)",
                        "2단계 평균(ms)",
                        "평균 반응시간 합(ms)"
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
                        "순위 기준: 1단계와 2단계 평균 반응시간의 합이 "
                        "작은 순"
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
        f"화살표 방향에 맞는 버튼을 최대한 빠르게 누르세요. (총 {TOTAL_TRIALS}회 진행)"
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
        f"화살표의 위치를 무시하고 기호의 방향대로 누르세요. (총 {TOTAL_TRIALS}회 진행)"
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

elif st.session_state.stage in[1,2]:

    if (
        st.session_state.feedback is None
        and st.session_state.start_time == 0.0
        and st.session_state.ready
    ):
        st.session_state.start_time = time.time()

    if st.session_state.stage == 1:
        st.success(
            f"▶ 1단계 진행 중 ({st.session_state.trial_count}/{TOTAL_TRIALS})"
        )
        st.write("화살표는 정가운데에 나타납니다.")

    else:
        st.warning(
            f"▶ 2단계 진행 중 ({st.session_state.trial_count}/{TOTAL_TRIALS})"
        )
        st.write("화살표 위치를 무시하고 방향대로 누르세요.")

    if st.session_state.feedback == "correct":
        st.markdown(
            "<h3 style='text-align:center;color:green;'>"
            "🟢 정답입니다!</h3>",
            unsafe_allow_html=True
        )

    elif st.session_state.feedback == "wrong":
        st.markdown(
            "<h3 style='text-align:center;color:red;'>"
            "🔴 틀렸습니다! 같은 문제를 다시 풀어주세요.</h3>",
            unsafe_allow_html=True
        )

    col_l, col_c, col_r = st.columns(3)

    if st.session_state.current_pos == "left":
        with col_l:
            st.markdown(
                f"<div class='arrow-box' style='text-align:center;"
                f"color:#007bff;font-size:80px;font-weight:bold;'>"
                f"{st.session_state.current_arrow}</div>",
                unsafe_allow_html=True
            )

    elif st.session_state.current_pos == "right":
        with col_r:
            st.markdown(
                f"<div class='arrow-box' style='text-align:center;"
                f"color:#007bff;font-size:80px;font-weight:bold;'>"
                f"{st.session_state.current_arrow}</div>",
                unsafe_allow_html=True
            )

    else:
        with col_c:
            st.markdown(
                f"<div class='arrow-box' style='text-align:center;"
                f"color:#28a745;font-size:80px;font-weight:bold;'>"
                f"{st.session_state.current_arrow}</div>",
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

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

    if user_choice is not None:

        if st.session_state.feedback is None:

            end_time = time.time()

            reaction_time = (
                end_time - st.session_state.start_time
            ) * 1000

            is_correct = (
                st.session_state.current_arrow == user_choice
            )

            # 2단계 전용 일치/불일치 조건 자동 판별 로직
            condition_type = "통제"
            if st.session_state.stage == 2:
                arrow = st.session_state.current_arrow
                pos = st.session_state.current_pos
                if (arrow == "←" and pos == "left") or (arrow == "→" and pos == "right"):
                    condition_type = "일치"
                else:
                    condition_type = "불일치"

            # 모든 응답 결과를 리스트에 누적 저장
            st.session_state.results.append({
                "단계": f"{st.session_state.stage}단계",
                "조건": condition_type,
                "반응시간(ms)": round(reaction_time, 2),
                "정답여부": is_correct
            })

            if is_correct:
                st.session_state.feedback = "correct"
                st.session_state.trial_count += 1
            else:
                st.session_state.feedback = "wrong"

            st.rerun()

    if st.session_state.feedback in ["correct", "wrong"]:

        time.sleep(0.4)

        if st.session_state.feedback == "correct":

            st.session_state.start_time = 0.0

            if st.session_state.trial_count >= TOTAL_TRIALS:

                if st.session_state.stage == 1:
                    st.session_state.stage = "전환기"
                    st.session_state.trial_count = 0

                elif st.session_state.stage == 2:
                    st.session_state.stage = "종료"

            else:
                generate_question()

        elif st.session_state.feedback == "wrong":
            # 오답을 선택한 경우 패널티로 동일 문항을 다시 출제
            st.session_state.start_time = time.time()

        st.session_state.feedback = None
        st.rerun()


# =========================================================
# 10. 실험 종료 및 결과 저장
# =========================================================

elif st.session_state.stage == "종료":

    st.balloons()

    st.success(
        "🎉 모든 테스트가 완료되었습니다! 참여해 주셔서 감사합니다."
    )

    # 데이터 통계 가치 분석 (정답 데이터 추출)
    stage1_times = [
        r["반응시간(ms)"]
        for r in st.session_state.results
        if r["단계"] == "1단계" and r["정답여부"]
    ]

    stage2_congruent_times = [
        r["반응시간(ms)"]
        for r in st.session_state.results
        if r["단계"] == "2단계" and r["조건"] == "일치" and r["정답여부"]
    ]

    stage2_incongruent_times = [
        r["반응시간(ms)"]
        for r in st.session_state.results
        if r["단계"] == "2단계" and r["조건"] == "불일치" and r["정답여부"]
    ]

    avg_stage1 = round(
        sum(stage1_times) / len(stage1_times), 2
    ) if stage1_times else 0

    avg_stage2_congruent = round(
        sum(stage2_congruent_times) / len(stage2_congruent_times), 2
    ) if stage2_congruent_times else 0

    avg_stage2_incongruent = round(
        sum(stage2_incongruent_times) / len(stage2_incongruent_times), 2
    ) if stage2_incongruent_times else 0

    # 2단계 전체 평균 산출 (랭킹 보드 정렬 동기화 용도)
    stage2_all_times = stage2_congruent_times + stage2_incongruent_times
    avg_stage2 = round(
        sum(stage2_all_times) / len(stage2_all_times), 2
    ) if stage2_all_times else 0

    # 사이먼 효과에 의한 순수 인지 갈등 지연 시간 산출
    simon_delay = round(avg_stage2_incongruent - avg_stage2_congruent, 2)

    total_answers = len(st.session_state.results)

    correct_count = sum(
        1 for r in st.session_state.results
        if r["정답여부"]
    )

    wrong_count = total_answers - correct_count

    accuracy = round(
        correct_count / total_answers * 100, 2
    ) if total_answers else 0

    # -----------------------------
    # Firebase 저장
    # -----------------------------

    if not st.session_state.db_saved:

        if db is None:
            st.error(
                "Firebase 연결 실패로 결과를 저장하지 못했습니다."
            )

        else:
            try:
                db.collection("experiment_results").add({
                    "nickname": st.session_state.nickname,
                    "stage1_avg": avg_stage1,
                    "stage2_avg": avg_stage2,
                    "stage2_congruent_avg": avg_stage2_congruent,
                    "stage2_incongruent_avg": avg_stage2_incongruent,
                    "simon_delay": simon_delay,
                    "total_answers": total_answers,
                    "correct_count": correct_count,
                    "wrong_count": wrong_count,
                    "accuracy": accuracy,
                    "created_at": firestore.SERVER_TIMESTAMP
                })

                st.session_state.db_saved = True

                st.success(
                    "✅ 실험 결과가 Firebase에 저장되었습니다!"
                )

            except Exception as e:
                st.error(f"Firebase 저장 실패: {e}")

    # -----------------------------
    # 결과 표시
    # -----------------------------

    st.markdown("## 📊 인지 속도 결과 분석")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🟢 1단계 (기준선)",
            f"{avg_stage1} ms"
        )

    with col2:
        st.metric(
            "🔵 2단계 일치 조건",
            f"{avg_stage2_congruent} ms"
        )

    with col3:
        st.metric(
            "🔴 2단계 불일치 조건",
            f"{avg_stage2_incongruent} ms"
        )

    st.markdown("---")

    m_col1, m_col2, m_col3 = st.columns(3)

    with m_col1:
        st.metric("🎯 정답률", f"{accuracy}%")

    with m_col2:
        st.metric("❌ 오답 횟수", f"{wrong_count}회")

    with m_col3:
        st.metric("⏳ 순수 인지 간섭 시간", f"{simon_delay} ms")

    st.info(
        f"💡 **분석 결과 :** 동일한 2단계 실험 내에서도 화살표 위치와 방향이 일치할 때보다, "
        f"불일치할 때 뇌가 혼란을 느껴 평균 **{simon_delay} ms** 만큼 반응이 지연되었습니다. "
        f"이것이 바로 《인코그니토》에서 말하는 무의식적 시각 위치 정보가 의식적 판단을 방해한 '사이먼 효과'의 증거입니다."
    )

    st.caption(
        "평균 반응시간은 정답 응답만을 대상으로 계산했습니다. "
        "정답률과 오답 횟수는 모든 응답을 대상으로 계산합니다."
    )

    if st.button(
        "🔄 처음부터 다시 도전하기",
        use_container_width=True
    ):
        st.session_state.stage = "시작화면"
        st.session_state.trial_count = 0
        st.session_state.start_time = 0.0
        st.session_state.current_arrow = "←"
        st.session_state.current_pos = "center"
        st.session_state.results = []
        st.session_state.feedback = None
        st.session_state.ready = False
        st.session_state.nickname = ""
        st.session_state.db_saved = False
        st.session_state.ranking_view = False

        # 닉네임 입력창도 초기화
