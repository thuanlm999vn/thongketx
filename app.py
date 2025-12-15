import streamlit as st
import datetime

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Tai Xiu Tracker Ultimate", page_icon="🎲", layout="centered")

# --- 2. GIAO DIỆN DARK MODE (CSS) ---
st.markdown("""
    <style>
    /* Nền đen */
    .stApp { background-color: #0e1117; color: white; }
    
    /* Box Thống Kê */
    .stat-box {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        margin-bottom: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .stat-num { font-size: 22px; font-weight: 800; color: #fff; }
    .stat-label { font-size: 11px; color: #9ca3af; text-transform: uppercase; margin-top: 2px; }
    
    /* Nút Tài/Xỉu to */
    .stButton>button {
        height: 60px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 18px;
        border: none;
        transition: transform 0.1s;
    }
    .stButton>button:active { transform: scale(0.98); }
    
    /* Lịch sử Visual */
    .dot {
        display: inline-block;
        width: 30px; height: 30px;
        line-height: 30px; text-align: center;
        border-radius: 50%;
        margin: 2px;
        font-weight: bold; font-size: 12px;
    }
    .bg-tai { background: linear-gradient(135deg, #ef4444, #b91c1c); color: white; }
    .bg-xiu { background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; }
    
    /* Ẩn footer */
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
""", unsafe_allow_html=True)

# --- 3. KHỞI TẠO DỮ LIỆU ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'init_tai' not in st.session_state:
    st.session_state.init_tai = 0
if 'init_xiu' not in st.session_state:
    st.session_state.init_xiu = 0

# --- 4. HÀM XỬ LÝ LOGIC ---
def add_result(res):
    st.session_state.history.insert(0, {'result': res, 'ts': datetime.datetime.now()})
    # Giữ lại 500 ván gần nhất
    st.session_state.history = st.session_state.history[:500]

def calculate_stats(history):
    # 1. Thống kê số lượng
    count_tai_new = len([x for x in history if x['result'] == 'Tài'])
    count_xiu_new = len([x for x in history if x['result'] == 'Xỉu'])
    
    # Cộng dồn với số nhập ban đầu
    total_tai = st.session_state.init_tai + count_tai_new
    total_xiu = st.session_state.init_xiu + count_xiu_new
    
    # 2. Thống kê Bệt & Nhảy (Dựa trên lịch sử nhập)
    total_bet_points = 0  # Tổng số lần 2 con giống nhau
    total_nhay_points = 0 # Tổng số lần 2 con khác nhau
    
    max_bet_streak = 0    # Dây bệt dài nhất
    max_nhay_streak = 0   # Dây nhảy dài nhất (cầu 1-1)
    
    if not history:
        return total_tai, total_xiu, 0, 0, 0, 0
        
    # Duyệt ngược từ cũ -> mới để tính Max Streak chính xác
    hist_rev = history[::-1]
    
    # -- Tính Tổng điểm Bệt/Nhảy --
    for i in range(len(hist_rev) - 1):
        if hist_rev[i]['result'] == hist_rev[i+1]['result']:
            total_bet_points += 1
        else:
            total_nhay_points += 1
            
    # -- Tính Max Streak (Dây dài nhất) --
    curr_bet = 1
    curr_nhay = 1
    
    # Mặc định nếu có ít nhất 1 ván thì max là 1
    if len(hist_rev) > 0:
        max_bet_streak = 1
        max_nhay_streak = 1
        
    for i in range(1, len(hist_rev)):
        prev = hist_rev[i-1]['result']
        curr = hist_rev[i]['result']
        
        # Max Bệt
        if curr == prev:
            curr_bet += 1
        else:
            max_bet_streak = max(max_bet_streak, curr_bet)
            curr_bet = 1
            
        # Max Nhảy (1-1)
        if curr != prev:
            curr_nhay += 1
        else:
            max_nhay_streak = max(max_nhay_streak, curr_nhay)
            curr_nhay = 1
            
    # Chốt sổ lần cuối
    max_bet_streak = max(max_bet_streak, curr_bet)
    max_nhay_streak = max(max_nhay_streak, curr_nhay)
    
    return total_tai, total_xiu, total_bet_points, total_nhay_points, max_bet_streak, max_nhay_streak

# --- 5. GIAO DIỆN CHÍNH ---

# === A. CÀI ĐẶT BAN ĐẦU ===
with st.expander("⚙️ NHẬP SỐ TÀI/XỈU CÓ SẴN (Lúc mới vào game)"):
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.init_tai = st.number_input("Tổng Tài game đang báo:", min_value=0, value=st.session_state.init_tai)
    with c2:
        st.session_state.init_xiu = st.number_input("Tổng Xỉu game đang báo:", min_value=0, value=st.session_state.init_xiu)

# === B. BẢNG THỐNG KÊ (DASHBOARD) ===
# Tính toán
t_tai, t_xiu, t_bet, t_nhay, m_bet, m_nhay = calculate_stats(st.session_state.history)

st.write("") # Khoảng cách
cols = st.columns(4)
with cols[0]:
    st.markdown(f"""<div class="stat-box" style="border-color:#ef4444"><div class="stat-num text-red-500" style="color:#fca5a5">{t_tai}</div><div class="stat-label">TỔNG TÀI</div></div>""", unsafe_allow_html=True)
with cols[1]:
    st.markdown(f"""<div class="stat-box" style="border-color:#3b82f6"><div class="stat-num text-blue-500" style="color:#93c5fd">{t_xiu}</div><div class="stat-label">TỔNG XỈU</div></div>""", unsafe_allow_html=True)
with cols[2]:
    st.markdown(f"""<div class="stat-box" style="border-color:#eab308"><div class="stat-num" style="color:#fde047">{t_bet} <span style="font-size:12px; color:#aaa">({m_bet})</span></div><div class="stat-label">BỆT (MAX)</div></div>""", unsafe_allow_html=True)
with cols[3]:
    st.markdown(f"""<div class="stat-box" style="border-color:#22c55e"><div class="stat-num" style="color:#86efac">{t_nhay} <span style="font-size:12px; color:#aaa">({m_nhay})</span></div><div class="stat-label">NHẢY (MAX)</div></div>""", unsafe_allow_html=True)

# === C. NÚT NHẬP LIỆU ===
st.write("")
b1, b2 = st.columns(2)
with b1:
    if st.button("🔴 TÀI", type="primary", use_container_width=True):
        add_result("Tài")
        st.rerun()
with b2:
    if st.button("🔵 XỈU", type="primary", use_container_width=True):
        add_result("Xỉu")
        st.rerun()

# Nhập nhanh
with st.expander("⌨️ Nhập chuỗi số nhanh"):
    txt_input = st.text_input("VD: 12 4 10 (Mới nhất bên trái)")
    if st.button("Lưu chuỗi"):
        if txt_input:
            nums = [int(s) for s in txt_input.split() if s.isdigit()]
            for n in nums[::-1]: # Đảo ngược để nạp đúng dòng thời gian
                r = 'Tài' if 11 <= n <= 18 else ('Xỉu' if 3 <= n <= 10 else None)
                if r: add_result(r)
            st.rerun()

# === D. DỰ ĐOÁN VUI (NÚT NHỎ) ===
st.write("")
col_pred, col_empty = st.columns([1, 2])
with col_pred:
    if st.button("🔮 Dự đoán vui"):
        if not st.session_state.history:
            st.toast("Chưa có dữ liệu để đoán!")
        else:
            # Logic dự đoán đơn giản
            last = st.session_state.history[0]['result']
            streak = 1
            for i in range(1, len(st.session_state.history)):
                if st.session_state.history[i]['result'] == last: streak += 1
                else: break
            
            if streak >= 4:
                msg = f"Đang bệt {last} {streak} tay -> Bẻ cầu đi!"
                icon = "⚡"
            elif streak == 1:
                msg = "Đang nhảy đẹp -> Theo cầu 1-1"
                icon = "🐰"
            else:
                msg = f"Cầu ngắn -> Theo tiếp {last}"
                icon = "🐢"
                
            st.toast(f"{icon} {msg}")

# === E. LỊCH SỬ VISUAL ===
if st.session_state.history:
    st.markdown("---")
    html_hist = '<div style="overflow-x: auto; white-space: nowrap; padding: 5px;">'
    for item in st.session_state.history:
        cls = "bg-tai" if item['result'] == "Tài" else "bg-xiu"
        val = "T" if item['result'] == "Tài" else "X"
        html_hist += f'<span class="dot {cls}">{val}</span>'
    html_hist += '</div>'
    st.markdown(html_hist, unsafe_allow_html=True)

    if st.button("↩️ Xóa ván cuối"):
        st.session_state.history.pop(0)
        st.rerun()
