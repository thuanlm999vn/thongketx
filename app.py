import streamlit as st
import pandas as pd

# --- CẤU HÌNH ---
st.set_page_config(page_title="Soi Cầu Pro (Lite)", page_icon="🎲", layout="centered")

# --- CSS TÙY CHỈNH ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold;}
    div[data-testid="stMetricValue"] { font-size: 24px; }
    .big-font { font-size: 18px !important; color: #333; }
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'init_tai' not in st.session_state:
    st.session_state.init_tai = 0
if 'init_xiu' not in st.session_state:
    st.session_state.init_xiu = 0

# --- HÀM LOGIC ---
def them_ket_qua(diem=None, ket_qua=None):
    if diem is not None:
        if diem > 0:
            if 11 <= diem <= 18: ket_qua = 'Tài'
            elif 3 <= diem <= 10: ket_qua = 'Xỉu'
    st.session_state.history.append({'diem': diem, 'ket_qua': ket_qua})

def phan_tich_cau(data):
    if not data: return 0, 0, 0, 0
    results = [x['ket_qua'] for x in data]
    
    # Tính Bệt
    bet_count, max_bet, current_bet = 0, 0, 1
    for i in range(1, len(results)):
        if results[i] == results[i-1]:
            current_bet += 1
        else:
            if current_bet >= 2:
                bet_count += 1
                max_bet = max(max_bet, current_bet)
            current_bet = 1
    if current_bet >= 2:
        bet_count += 1
        max_bet = max(max_bet, current_bet)

    # Tính Nhảy
    nhay_count, max_nhay, current_nhay = 0, 0, 1
    for i in range(1, len(results)):
        if results[i] != results[i-1]:
            current_nhay += 1
        else:
            if current_nhay >= 3:
                nhay_count += 1
                max_nhay = max(max_nhay, current_nhay)
            current_nhay = 1
    if current_nhay >= 3:
        nhay_count += 1
        max_nhay = max(max_nhay, current_nhay)
        
    return bet_count, max_bet, nhay_count, max_nhay

# --- GIAO DIỆN CHÍNH ---
st.title("🎲 SUPER SOI CẦU (LITE)")

# === PHẦN 1: CÀI ĐẶT THÔNG SỐ BAN ĐẦU ===
with st.expander("⚙️ CÀI ĐẶT TỔNG TÀI/XỈU BAN ĐẦU", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.init_tai = st.number_input("Tổng Tài hiện tại (trên game):", min_value=0, value=st.session_state.init_tai)
    with c2:
        st.session_state.init_xiu = st.number_input("Tổng Xỉu hiện tại (trên game):", min_value=0, value=st.session_state.init_xiu)
    st.caption("💡 Nhập số lượng Tài/Xỉu bạn nhìn thấy trên màn hình game để thống kê tổng chính xác hơn.")

# === PHẦN 2: ẢNH THAM KHẢO ===
with st.expander("📸 MỞ ẢNH ĐỂ NHÌN & NHẬP", expanded=True):
    uploaded_file = st.file_uploader("Tải ảnh game lên (Chỉ để xem):", type=['jpg', 'png', 'jpeg'])
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Nhìn vào ảnh này để nhập liệu bên dưới 👇", use_container_width=True)

# === PHẦN 3: NHẬP LIỆU ===
st.divider()
st.caption("👇 BẤM ĐỂ NHẬP KẾT QUẢ MỚI")
btn1, btn2, btn3 = st.columns([1, 1, 1.5])

with btn1:
    if st.button("🔴 TÀI", type="primary"):
        them_ket_qua(ket_qua="Tài", diem=0)
        st.rerun()
with btn2:
    if st.button("🔵 XỈU"):
        them_ket_qua(ket_qua="Xỉu", diem=0)
        st.rerun()
with btn3:
    with st.popover("🔢 Nhập Điểm Số"):
        num = st.number_input("Điểm:", 3, 18, step=1)
        if st.button("Lưu Điểm"):
            them_ket_qua(diem=int(num))
            st.rerun()

# === PHẦN 4: SỬA LỖI ===
if len(st.session_state.history) > 0:
    with st.expander("🛠️ SỬA / XÓA (5 ván gần nhất)"):
        if st.button("↩️ Xóa ván vừa nhập (Undo)"):
            st.session_state.history.pop()
            st.rerun()
        
        # Form sửa
        cnt = len(st.session_state.history)
        start = max(0, cnt - 5)
        with st.form("sua_loi"):
            for i in range(cnt - 1, start - 1, -1):
                item = st.session_state.history[i]
                c_idx, c_k, c_d = st.columns([1, 2, 2])
                with c_idx: st.write(f"#{i+1}")
                with c_k:
                    idx = 0 if item['ket_qua'] == 'Tài' else 1
                    st.session_state[f"k_{i}"] = st.selectbox("", ["Tài", "Xỉu"], index=idx, key=f"sel_{i}", label_visibility="collapsed")
                with c_d:
                    v_d = item['diem'] if item['diem'] else 0
                    st.session_state[f"d_{i}"] = st.number_input("", value=v_d, min_value=0, max_value=18, key=f"num_{i}", label_visibility="collapsed")
            
            if st.form_submit_button("💾 Lưu thay đổi"):
                for i in range(cnt - 1, start - 1, -1):
                    st.session_state.history[i]['ket_qua'] = st.session_state[f"sel_{i}"]
                    val = st.session_state[f"num_{i}"]
                    st.session_state.history[i]['diem'] = val if val > 0 else None
                st.rerun()

# === PHẦN 5: THỐNG KÊ (DASHBOARD) ===
st.divider()

# Tính toán tổng hợp
sl_tai_nhap = len([x for x in st.session_state.history if x['ket_qua'] == 'Tài'])
sl_xiu_nhap = len([x for x in st.session_state.history if x['ket_qua'] == 'Xỉu'])

# Tổng = Số ban đầu + Số vừa nhập thêm
tong_tai = st.session_state.init_tai + sl_tai_nhap
tong_xiu = st.session_state.init_xiu + sl_xiu_nhap
tong_cong = tong_tai + tong_xiu

# Hiển thị
m1, m2, m3 = st.columns(3)
m1.metric("TỔNG SỐ VÁN", tong_cong)

if tong_cong > 0:
    pct_tai = (tong_tai / tong_cong) * 100
    pct_xiu = (tong_xiu / tong_cong) * 100
    m2.metric("🔴 TỔNG TÀI", f"{tong_tai}", f"{pct_tai:.1f}%")
    m3.metric("🔵 TỔNG XỈU", f"{tong_xiu}", f"{pct_xiu:.1f}%")
else:
    m2.metric("🔴 TỔNG TÀI", 0)
    m3.metric("🔵 TỔNG XỈU", 0)

# Phân tích Cầu (Chỉ tính trên lịch sử nhập, không tính số ban đầu vì không biết thứ tự)
if len(st.session_state.history) > 0:
    st.caption(f"--- Phân tích Cầu (Dựa trên {len(st.session_state.history)} ván vừa nhập) ---")
    bet, max_bet, nhay, max_nhay = phan_tich_cau(st.session_state.history)
    
    k1, k2 = st.columns(2)
    k1.info(f"🐍 Bệt dài nhất: {max_bet}")
    k2.warning(f"⚡ Nhảy dài nhất: {max_nhay}")
    
    st.write("##### 📜 Biểu đồ:")
    icons = ["🔴" if h['ket_qua'] == 'Tài' else "🔵" for h in st.session_state.history]
    st.text_area("", "  ➜  ".join(icons), height=100)
