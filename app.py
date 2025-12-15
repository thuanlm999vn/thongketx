import streamlit as st
import pandas as pd

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Soi Cầu Pro", page_icon="🎲", layout="centered")

# --- CSS GIAO DIỆN ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold;}
    div[data-testid="stMetricValue"] { font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU ---
if 'history' not in st.session_state:
    st.session_state.history = []

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
st.title("🎲 SUPER SOI CẦU ONLINE")

# === PHẦN MỚI: UPLOAD ẢNH ===
with st.expander("📸 MỞ ẢNH SOII CẦU", expanded=True):
    uploaded_file = st.file_uploader("Chọn ảnh chụp màn hình game:", type=['jpg', 'png', 'jpeg'])
    if uploaded_file is not None:
        # Hiển thị ảnh để người dùng nhìn
        st.image(uploaded_file, caption="Ảnh bạn vừa tải lên", use_container_width=True)
        st.info("💡 Mẹo: Nhìn vào ảnh trên và bấm nút nhập liệu bên dưới cho nhanh!")

# === PHẦN NHẬP LIỆU ===
st.divider()
st.caption("👇 NHẬP KẾT QUẢ VÁN MỚI")
c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    if st.button("🔴 TÀI", type="primary"):
        them_ket_qua(ket_qua="Tài", diem=0)
        st.rerun()
with c2:
    if st.button("🔵 XỈU"):
        them_ket_qua(ket_qua="Xỉu", diem=0)
        st.rerun()
with c3:
    with st.popover("🔢 Nhập Số"):
        num = st.number_input("Điểm:", 3, 18, step=1)
        if st.button("Lưu"):
            them_ket_qua(diem=int(num))
            st.rerun()

# === PHẦN SỬA LỖI ===
if len(st.session_state.history) > 0:
    with st.expander("🛠️ SỬA / XÓA (5 Ván gần nhất)"):
        if st.button("↩️ Xóa ván cuối (Undo)"):
            st.session_state.history.pop()
            st.rerun()
        
        # Form sửa chi tiết
        so_luong = len(st.session_state.history)
        start = max(0, so_luong - 5)
        with st.form("sua_loi"):
            for i in range(so_luong - 1, start - 1, -1):
                item = st.session_state.history[i]
                cc1, cc2, cc3 = st.columns([1, 2, 2])
                with cc1: st.write(f"#{i+1}")
                with cc2: 
                    idx = 0 if item['ket_qua'] == 'Tài' else 1
                    st.session_state[f"k_{i}"] = st.selectbox("", ["Tài", "Xỉu"], index=idx, key=f"s_{i}", label_visibility="collapsed")
                with cc3:
                    d_val = item['diem'] if item['diem'] else 0
                    st.session_state[f"d_{i}"] = st.number_input("", value=d_val, min_value=0, max_value=18, key=f"n_{i}", label_visibility="collapsed")
            
            if st.form_submit_button("Lưu thay đổi"):
                for i in range(so_luong - 1, start - 1, -1):
                    new_k = st.session_state[f"s_{i}"]
                    new_d = st.session_state[f"n_{i}"]
                    st.session_state.history[i]['ket_qua'] = new_k
                    st.session_state.history[i]['diem'] = new_d if new_d > 0 else None
                st.rerun()

# === DASHBOARD ===
if len(st.session_state.history) > 0:
    st.divider()
    df = pd.DataFrame(st.session_state.history)
    tong = len(df)
    tai = len(df[df['ket_qua'] == 'Tài'])
    xiu = len(df[df['ket_qua'] == 'Xỉu'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Tổng ván", tong)
    m2.metric("Tài 🔴", f"{tai}", f"{(tai/tong)*100:.0f}%")
    m3.metric("Xỉu 🔵", f"{xiu}", f"{(xiu/tong)*100:.0f}%")
    
    bet, max_bet, nhay, max_nhay = phan_tich_cau(st.session_state.history)
    k1, k2 = st.columns(2)
    k1.info(f"🐍 Bệt dài nhất: {max_bet}")
    k2.warning(f"⚡ Nhảy dài nhất: {max_nhay}")
    
    st.write("##### 📜 Lịch sử cầu:")
    icons = ["🔴" if h['ket_qua'] == 'Tài' else "🔵" for h in st.session_state.history]
    st.text_area("", "  ➜  ".join(icons), height=100)
