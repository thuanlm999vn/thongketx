import streamlit as st
import pandas as pd

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Soi Cầu Pro", page_icon="🎲", layout="centered")

# --- CSS TÙY CHỈNH ---
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
        if diem > 0: # Nếu nhập số cụ thể
            if 11 <= diem <= 18: ket_qua = 'Tài'
            elif 3 <= diem <= 10: ket_qua = 'Xỉu'
    st.session_state.history.append({'diem': diem, 'ket_qua': ket_qua})

def phan_tich_cau(data):
    if not data: return 0, 0, 0, 0
    results = [x['ket_qua'] for x in data]
    
    # 1. Tính Bệt
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

    # 2. Tính Nhảy (1-1)
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

# 1. KHU VỰC NHẬP LIỆU
st.info("👇 Nhập kết quả ván mới nhất tại đây")
c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    if st.button("🔴 TÀI", type="primary"):
        them_ket_qua(ket_qua="Tài", diem=0) # 0 nghĩa là không rõ điểm
        st.rerun()
with c2:
    if st.button("🔵 XỈU"):
        them_ket_qua(ket_qua="Xỉu", diem=0)
        st.rerun()
with c3:
    # Nhập số nhanh
    with st.popover("🔢 Nhập Số"):
        num = st.number_input("Điểm số:", 3, 18, step=1)
        if st.button("Lưu Số"):
            them_ket_qua(diem=int(num))
            st.rerun()

# 2. KHU VỰC SỬA LỖI
if len(st.session_state.history) > 0:
    with st.expander("🛠️ SỬA / XÓA (5 Ván gần nhất)"):
        if st.button("↩️ Xóa ván vừa nhập (Undo)"):
            st.session_state.history.pop()
            st.rerun()
        st.divider()
        st.write("Hoặc chỉnh sửa chi tiết:")
        so_luong = len(st.session_state.history)
        start_index = max(0, so_luong - 5)
        with st.form("form_sua_loi"):
            for i in range(so_luong - 1, start_index - 1, -1):
                item = st.session_state.history[i]
                c_idx, c_kq, c_diem = st.columns([1, 2, 2])
                with c_idx: st.write(f"**Ván {i+1}**")
                with c_kq:
                    idx_val = 0 if item['ket_qua'] == 'Tài' else 1
                    new_kq = st.selectbox("KQ", ["Tài", "Xỉu"], index=idx_val, key=f"kq_{i}", label_visibility="collapsed")
                with c_diem:
                    val_diem = item['diem'] if item['diem'] is not None else 0
                    new_diem = st.number_input("Điểm", value=val_diem, min_value=0, max_value=18, key=f"d_{i}", label_visibility="collapsed")
            submit_sua = st.form_submit_button("💾 Lưu Thay Đổi")
            if submit_sua:
                for i in range(so_luong - 1, start_index - 1, -1):
                    k_kq = st.session_state[f"kq_{i}"]
                    k_diem = st.session_state[f"d_{i}"]
                    st.session_state.history[i]['ket_qua'] = k_kq
                    st.session_state.history[i]['diem'] = k_diem if k_diem > 0 else None
                st.success("Đã sửa thành công!")
                st.rerun()

# 3. DASHBOARD THỐNG KÊ
st.divider()
if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    tong = len(df)
    tai = len(df[df['ket_qua'] == 'Tài'])
    xiu = len(df[df['ket_qua'] == 'Xỉu'])
    
    # 3.1. Tổng quan
    m1, m2, m3 = st.columns(3)
    m1.metric("Tổng", tong)
    m2.metric("Tài 🔴", f"{tai}", delta=f"{tai/tong*100:.0f}%")
    m3.metric("Xỉu 🔵", f"{xiu}", delta=f"{xiu/tong*100:.0f}%")
    
    # 3.2. Phân tích Cầu
    bet, max_bet, nhay, max_nhay = phan_tich_cau(st.session_state.history)
    st.caption("--- Phân tích Cầu ---")
    k1, k2 = st.columns(2)
    k1.info(f"🐍 Bệt dài nhất: **{max_bet}**")
    k2.warning(f"⚡ Nhảy dài nhất: **{max_nhay}**")
    
    # 3.3. Log Hình ảnh
    st.write("##### 📜 Lịch sử cầu:")
    icons = []
    for h in st.session_state.history:
        d = h['diem'] if h['diem'] and h['diem'] > 0 else ""
        icon = "🔴" if h['ket_qua'] == 'Tài' else "🔵"
        icons.append(f"{icon}{d}")
    st.text_area("", "  ➜  ".join(icons), height=80, disabled=True)
else:
    st.warning("Chưa có dữ liệu. Hãy nhập ván đầu tiên!")