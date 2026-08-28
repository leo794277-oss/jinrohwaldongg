import streamlit as st
import time
import random

# --- 1. 페이지 기본 설정 및 제목 ---
st.set_page_config(page_title="뇌 인지 충돌 실험", layout="centered")
st.title("🧠 화살표 인지 충돌 시뮬레이터")
st.write("⚠️ 나타난 위치는 무시하고, 오직 **[화살표 기호의 방향]**대로 아래 버튼을 가장 빠르게 터치하세요!")

# --- 2. 실험 상태(데이터) 저장소 초기화 ---
if "start_time" not in st.session_state:
    st.session_state.start_time = 0.0
if "results" not in st.session_state:
    st.session_state.results = []
if "current_arrow" not in st.session_state:
    st.session_state.current_arrow = "←"
if "current_pos" not in st.session_state:
    st.session_state.current_pos = "left"

# --- 3. 문제 출제 함수 (랜덤 믹스) ---
def generate_new_question():
    st.session_state.current_arrow = random.choice(["←", "→"])
    st.session_state.current_pos = random.choice(["left", "right"])
    st.session_state.start_time = time.time()  # 화살표가 뜬 순간의 절대 시간 기록

# 맨 처음 프로그램을 켰을 때 첫 문제 출제
if st.session_state.start_time == 0.0:
    generate_new_question()

# --- 4. 자극 화면 구현 (화살표 모양과 위치 정렬) ---
col_left, col_right = st.columns(2)

if st.session_state.current_pos == "left":
    with col_left:
        st.markdown(f"<h1 style='text-align: left; color: #007bff; font-size: 80px;'>{st.session_state.current_arrow}</h1>", unsafe_allow_html=True)
else:
    with col_right:
        st.markdown(f"<h1 style='text-align: right; color: #007bff; font-size: 80px;'>{st.session_state.current_arrow}</h1>", unsafe_allow_html=True)

st.write("---") # 구분선

# --- 5. 친구들이 터치할 큰 버튼 2개 배치 ---
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.button("👈 LEFT (왼쪽)", use_container_width=True):
        end_time = time.time()
        reaction_time = (end_time - st.session_state.start_time) * 1000 # ms 단위 변환
        
        # 판정: 왼쪽 버튼을 누른 게 맞으므로 화살표 기호가 '←'였으면 정답
        is_correct = (st.session_state.current_arrow == "←")
        
        # 일치 여부 판정 (모양과 위치가 일치하는지)
        is_congruent = (st.session_state.current_arrow == "←" and st.session_state.current_pos == "left") or (st.session_state.current_arrow == "→" and st.session_state.current_pos == "right")
        
        # 데이터 누적
        st.session_state.results.append({
            "조건": "일치" if is_congruent else "불일치",
            "반응시간(ms)": round(reaction_time, 2),
            "정답여부": is_correct
        })
        
        generate_new_question()
        st.rerun()

with btn_col2:
    if st.button("👉 RIGHT (오른쪽)", use_container_width=True):
        end_time = time.time()
        reaction_time = (end_time - st.session_state.start_time) * 1000
        
        is_correct = (st.session_state.current_arrow == "→")
        is_congruent = (st.session_state.current_arrow == "←" and st.session_state.current_pos == "left") or (st.session_state.current_arrow == "→" and st.session_state.current_pos == "right")
        
        st.session_state.results.append({
            "조건": "일치" if is_congruent else "불일치",
            "반응시간(ms)": round(reaction_time, 2),
            "정답여부": is_correct
        })
        
        generate_new_question()
        st.rerun()

# --- 6. 실시간 데이터 기록 화면에 보여주기 (확인용) ---
st.write("### 📊 현재 누적된 실험 기록")
st.write(st.session_state.results)
