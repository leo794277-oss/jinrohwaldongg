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
        service_account_info = dict(st.secrets["firebase_service_account"])
        if "private_key" in service_account_info:
            service_account_info["private_key"] = service_account_info["private_key"].replace("\\n", "\n")
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

# 실험 문항 수 설정 (데이터 신뢰도를 위해 10회로 상향)
TOTAL_TRIALS = 10

# =========================================================
# 2. 문제 출제
# =========================================================
def generate_question():
    st.session_state.current_arrow = random.choice(["←", "→"])
    if st.session_state.stage == 1:
        st.session_state.current_pos = "center"
    elif st.session_state.stage == 2:
        st.session_state.current_pos = random.choice(["left", "right"])

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
    .stApp {{ background-color: {bg_color} !important; transition: background-color 0.1s; }}
    .arrow-box {{ display: inline-block; width: 100%; animation: arrow-pop 0.3s ease-in-out; }}
    @keyframes arrow-pop {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.3); }} 100% {{ transform: scale(1); }} }}
    div[data-testid="stTextInput"] input {{ background-color: #ffffff !important; color: #222222 !important; border: 2px solid #4A90E2 !important; border-radius: 10px !important; min-height: 52px !important; font-size: 18px !important; padding: 10px 14px !important; }}
    div[data-testid="stTextInput"] label {{ color: #222222 !important; font-size: 17px !important; font-weight: 700 !important; }}
    div[data-testid="stTextInput"] input::placeholder {{ color: #777777 !important; opacity: 1 !important; }}
    div[data-testid="stTextInput"] input:focus {{ border-color: #1D65C1 !important; box-shadow: 0 0 0 2px rgba(29, 101, 193, 0.2) !important; }}
    div[data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{ min-width: 0 !important; flex: 1 1 0% !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 4. 카운트다운 (완벽 수정 완료)
# =========================================================
def run_countdown():
    placeholder = st.empty()
    for i in:[3, 2, 1]
        placeholder.markdown(f'<h1 style="text-align:center;font-size:100px;color:#ff4b4b;">{i}</h1>', unsafe_allow_html=True)
        time.sleep(1)
    placeholder.markdown('<h1 style="text-align:center;font-size:100px;color:#28a745;">START!</h1>', unsafe_allow_html=True)
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
    st.info("👋 뇌 인지 간섭 실험 사이트에 오신 것을 환영합니다.")
    nickname = st.text_input("닉네임을 입력하세요", placeholder="여기에 닉네임을 입력하세요", max_chars=20, key="nickname_input")
    st.write("본 실험은 스마트폰 모바일 터치 환경에 최적화되어 있습니다.")
    st.write("정밀한 측정을 위해 스마트폰 진동 및 소리를 켜주세요.")

    if st.button("🚀 실험 홈 진입하기", use_container_width=True):
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

    st.markdown("---")
    st.subheader("🏆 실험 랭킹")

    if st.button("🏆 랭킹 보기", use_container_width=True):
        st.session_state.ranking_view = True

    if st.session_state.ranking_view:
        if db is None:
            st.error("Firebase에 연결되지 않았습니다.")
        else:
            try:
                docs = db.collection("experiment_results").stream()
                ranking_data = []
                for doc in docs:
                    data = doc.to_dict() or {}
                    if "nickname" not in data or "stage1_avg" not in data or "stage2_avg" not in data:
                        continue
                    stage1_avg = float(data["stage1_avg"])
                    stage2_avg = float(data["stage2_avg"])
                    ranking_data.append({
                        "닉네임": data["nickname"],
                        "1단계 평균(ms)": stage1_avg,
                        "2단계 평균(ms)": stage2_avg,
                        "평균 반응시간 합(ms)": round(stage1_avg + stage2_avg, 2)
                    })

                ranking_data.sort(key=lambda x: x["평균 반응시간 합(ms)"])

                if ranking_data:
                    for i, item in enumerate(ranking_data, start=1):
                        item["순위"] = i
                    columns = ["순위", "닉네임", "1단계 평균(ms)", "2단계 평균(ms)", "평균 반응시간 합(ms)"]
                    st.dataframe([{col: item[col] for col in columns} for item in ranking_data], use_container_width=True, hide_index=True)
                    st.caption("순위 기준: 1단계와 2단계 평균 반응시간의 합이 작은 순")
                else:
                    st.info("아직 저장된 실험 기록이 없습니다.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 랭킹 새로고침", use_container_width=True): st.rerun()
                with col2:
                    if st.button("랭킹 닫기", use_container_width=True):
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
    st.info("← 이면 LEFT, → 이면 RIGHT 버튼을 누르세요.")
    st.write(f"화살표 방향에 맞는 버튼을 최대한 빠르게 누르세요. (총 {TOTAL_TRIALS}회 진행)")

    if st.button("🚀 1단계 시작하기", use_container_width=True):
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
    st.write("화살표가 화면 왼쪽 또는 오른쪽에 나타납니다.")
    st.warning(f"화살표의 위치를 무시하고 기호의 방향대로 누르세요. (총 {TOTAL_TRIALS}회 진행)")

    if st.button("🚀 2단계 시작하기", use_container_width=True):
        run_countdown()
        st.session_state.stage = 2
        st.session_state.trial_count = 0
        st.session_state.feedback = None
        st.session_state.ready = True
        generate_question()
        st.session_state.start_time = time.time()
        st.rerun()

# =========================================================
# 9. 실험 진행 (완벽 수정 완료)
# =========================================================
elif st.session_state.stage in:[1, 2]
    if st.session_state.feedback is None and st.session_state.start_time == 0.0 and st.session_state.ready:
        st.session_state.start_time = time.time()

    if st.session_state.stage == 1:
        st.success(f"▶ 1단계 진행 중 ({st.session_state.trial_count}/{TOTAL_TRIALS})")
        st.write("화살표는 정가운데에 나타납니다.")
    else:
        st.warning(f"▶ 2단계 진행 중 ({st.session_state.trial_count}/{TOTAL_TRIALS})")
        st.write("화살표 위치를 무시하고 방향대로 누르세요.")

    if st.session_state.feedback == "correct":
        st.markdown("<h3 style='text-align:center;color:green;'>🟢 정답입니다!</h3>", unsafe_allow_html=True)
    elif st.session_state.feedback == "wrong":
        st.markdown("<h3 style='text-align:center;color:red;'>🔴 틀렸습니다! 같은 문제를 다시 풀어주세요.</h3>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns(3)
    if st.session_state.current_pos == "left":
