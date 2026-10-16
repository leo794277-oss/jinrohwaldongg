
import streamlit as st
import time
import random
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core.exceptions import AlreadyExists


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
    "nickname_reserved": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 2. 닉네임 중복 방지
# =========================================================

def get_nickname_id(nickname):
    """대소문자 차이를 무시하는 닉네임 고유 ID."""
    normalized = nickname.strip().casefold()

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def reserve_nickname(nickname):
    """
    Firestore 문서 생성으로 닉네임을 원자적으로 선점한다.
    이미 사용 중이면 False를 반환한다.
    """
    normalized = nickname.strip().casefold()

    # 기능 추가 이전에 저장된 실험 기록도 확인
    old_records = db.collection(
        "experiment_results"
    ).stream()

    for doc in old_records:
        data = doc.to_dict() or {}
        old_nickname = str(data.get("nickname", "")).strip()

        if old_nickname.casefold() == normalized:
            return False

    # 닉네임을 별도 컬렉션에 등록
    nickname_ref = db.collection(
        "nicknames"
    ).document(get_nickname_id(nickname))

    try:
        nickname_ref.create({
            "nickname": nickname.strip(),
            "normalized_nickname": normalized,
            "created_at": firestore.SERVER_TIMESTAMP
        })

        return True

    except AlreadyExists:
        return False


# =========================================================
# 3. 문제 출제
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
# 4. 화면 효과
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
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 5. 카운트다운
# =========================================================

def run_countdown():
    placeholder = st.empty()

    for i in [3, 2, 1]:
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
# 6. 제목 및 사이드바
# =========================================================

st.title("🧠 단계별 인지 간섭 시뮬레이터")

if db is not None:
    st.sidebar.success("Firebase 연결 성공")
else:
    st.sidebar.error(f"Firebase 연결 실패: {firebase_error}")


# =========================================================
# 7. 시작 화면 + 랭킹
# =========================================================

if st.session_state.stage == "시작화면":

    st.info(
        "👋 뇌 인지 간섭 실험 사이트에 오신 것을 환영합니다."
    )

    nickname = st.text_input(
        "닉네임을 입력하세요",
        max_chars=20
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

        elif db is None:
            st.error(
                "Firebase에 연결할 수 없습니다. "
                "설정을 확인한 뒤 다시 시도해주세요."
            )

        else:
            try:
                reserved = reserve_nickname(clean_nickname)

                if not reserved:
                    st.error(
                        "이미 사용 중인 닉네임입니다. "
                        "다른 닉네임을 입력해주세요."
                    )

                else:
                    st.session_state.nickname = clean_nickname
                    st.session_state.nickname_reserved = True
                    st.session_state.stage = "1단계안내"
                    st.session_state.db_saved = False
                    st.session_state.results = []
                    st.session_state.trial_count = 0
                    st.session_state.feedback = None
                    st.session_state.ready = False
                    st.rerun()

            except Exception as e:
                st.error(f"닉네임 확인 실패: {e}")

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
                        or "delay" not in data
                    ):
                        continue

                    ranking_data.append({
                        "닉네임": data["nickname"],
                        "정답률(%)": float(
                            data.get("accuracy", 0)
                        ),
                        "오답 횟수": int(
                            data.get("wrong_count", 0)
                        ),
                        "2단계 평균(ms)": float(
                            data["stage2_avg"]
                        ),
                        "1단계 평균(ms)": float(
                            data["stage1_avg"]
                        ),
                        "지연시간(ms)": float(
                            data["delay"]
                        )
                    })

                # 정답률 높은 순 → 오답 적은 순 → 반응시간 빠른 순
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
# 8. 1단계 안내
# =========================================================

elif st.session_state.stage == "1단계안내":

    st.success("🟢 1단계 통제 실험")

    st.markdown("### 📢 1단계 규칙")

    st.write(
        "화살표가 화면 정가운데에 나타납니다."
    )

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
# 9. 1단계 → 2단계 전환
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
# 10. 실험 진행
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

    else:
        st.warning(
            f"▶ 2단계 진행 중 ({st.session_state.trial_count}/5)"
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
        if st.button("👈 LEFT (왼쪽)", use_container_width=True):
            user_choice = "←"

    with btn_col2:
        if st.button("👉 RIGHT (오른쪽)", use_container_width=True):
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

            # 모든 응답을 저장해 정답률과 오답 횟수 계산
            st.session_state.results.append({
                "단계": f"{st.session_state.stage}단계",
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

            if st.session_state.trial_count >= 5:

                if st.session_state.stage == 1:
                    st.session_state.stage = "전환기"
                    st.session_state.trial_count = 0

                elif st.session_state.stage == 2:
                    st.session_state.stage = "종료"

            else:
                generate_question()

        elif st.session_state.feedback == "wrong":
            # 오답이면 같은 문제를 다시 시도
            st.session_state.start_time = time.time()

        st.session_state.feedback = None
        st.rerun()


# =========================================================
# 11. 실험 종료 및 결과 저장
# =========================================================

elif st.session_state.stage == "종료":

    st.balloons()

    st.success(
        "🎉 모든 테스트가 완료되었습니다! 참여해 주셔서 감사합니다."
    )

    # 정답인 응답의 반응시간만 평균 계산에 사용
    stage1_times = [
        r["반응시간(ms)"]
        for r in st.session_state.results
        if r["단계"] == "1단계" and r["정답여부"]
    ]

    stage2_times = [
        r["반응시간(ms)"]
        for r in st.session_state.results
        if r["단계"] == "2단계" and r["정답여부"]
    ]

    avg_stage1 = round(
        sum(stage1_times) / len(stage1_times), 2
    ) if stage1_times else 0

    avg_stage2 = round(
        sum(stage2_times) / len(stage2_times), 2
    ) if stage2_times else 0

    delay = round(avg_stage2 - avg_stage1, 2)

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
                    "delay": delay,
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

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "🟢 1단계 평균 반응시간",
            f"{avg_stage1} ms"
        )

    with col2:
        st.metric(
            "🔵 2단계 평균 반응시간",
            f"{avg_stage2} ms"
        )

    st.metric("🎯 정답률", f"{accuracy}%")
    st.metric("❌ 오답 횟수", f"{wrong_count}회")

    st.write(
        f"공간 간섭에 따른 평균 반응시간 차이: {delay} ms"
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
        st.session_state.nickname_reserved = False

        st.rerun()
