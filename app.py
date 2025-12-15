import streamlit as st
import pandas as pd

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Soi Cầu Pro", page_icon="📊", layout="wide")

# --- CSS TÙY CHỈNH (GIAO DIỆN ĐẸP) ---
st.markdown("""
    <style>
    /* Chỉnh nút bấm to đẹp */
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; font-size: 16px; }
    
    /* Màu sắc cho Tài/Xỉu */
    .tai-text { color: #e74c3c; font-weight: bold; font-size: 20px; }
    .xiu-text { color: #3498db; font-weight: bold; font-size: 20px; }
    
    /* Box thống kê */
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: bold; }
    
    /* Căn chỉnh lại padding */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
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

def phan_tich_cau_chi_tiet(data):
    if not data: return 0, 0, 0, 0
    results = [x['ket_qua'] for x in data]
    
    # 1. PHÂN TÍCH CẦU BỆT (Dây >= 2 ván giống nhau)
    bet_count = 0      # Tổng số lần xuất hiện dây bệt
    max_bet = 0        # Dây bệt dài nhất
    curr_bet = 1
    
    # 2. PHÂN TÍCH CẦU NHẢY (Dây 1-1 >= 3 nhịp, VD: T-X-T)
    nhay_count = 0     # Tổng số lần xuất hiện cầu nhảy
    max_nhay = 0       # Cầu nhảy dài nhất
    curr_nhay = 1
    
    # Duyệt loop để đếm
    for i in range(1, len(results)):
        # --- Logic Bệt ---
        if results[i] == results[i-1]:
            curr_bet += 1
        else:
            if curr_bet >= 2: 
                bet_count += 1
                max_bet = max(max_bet, curr_bet)
            curr_bet = 1 # Reset
            
        # --- Logic Nhảy ---
        if results[i] != results[i-1]:
            curr_nhay += 1
        else:
            if curr_nhay >= 3:
                nhay_count += 1
                max_nhay = max(max_nhay, curr_nhay)
            curr_nhay = 1 # Reset

    # Check phần đuôi cuối cùng sau khi hết vòng lặp
    if curr_bet >= 2: 
        bet_count += 1
        max_bet = max(max_bet, curr_bet)
    
    if curr_nhay >= 3:
        nhay_count += 1
        max_nhay = max(max_nhay, curr_nhay)
        
    return bet_count, max_bet, nhay_count, max_nhay

# --- GIAO DIỆN CHÍNH ---

# Header chia cột để gọn gàng
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title("📊 SOFTSOI DASHBOARD")
with col_header_2:
    if st.button("🗑️ Reset Dữ Liệu"):
        st.session_state.history = []
        st.session_state.init_tai = 0
        st.session_state.init_xiu = 0
        st.rerun()

st.divider()

# === KHU VỰC 1: NHẬP LIỆU (Đưa lên đầu cho tiện tay) ===
col_input_1, col_input_2 = st.columns([1, 2])

with col_input_1:
    st.caption("📷 ẢNH THAM KHẢO")
    uploaded_file = st.file_uploader("", type=['jpg', 'png'], label_visibility="collapsed")
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)

with col_input_2:
    st.caption("✍️ NHẬP KẾT QUẢ VÁN MỚI")
    
    # Hàng nút bấm to
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔴 TÀI (Big)", type="primary"):
            them_ket_qua(ket_qua="Tài", diem=0)
            st.rerun()
    with b2:
        if st.button("🔵 XỈU (Small)"):
            them_ket_qua(ket_qua="Xỉu", diem=0)
            st.rerun()
            
    # Hàng nhập số & Cài đặt ban đầu
    st.write("") # Spacer
    c_num, c_set = st.columns([1, 1])
    with c_num:
        with st.popover("🔢 Nhập Điểm Số"):
            num = st.number_input("Điểm:", 3, 18)
            if st.button("Lưu Điểm"):
                them_ket_qua(diem=int(num))
                st.rerun()
    with c_set:
        with st.popover("⚙️ Cài Số Tài/Xỉu Gốc"):
            st.session_state.init_tai = st.number_input("Tổng Tài gốc:", 0, value=st.session_state.init_tai)
            st.session_state.init_xiu = st.number_input("Tổng Xỉu gốc:", 0, value=st.session_state.init_xiu)
            st.caption("Nhập số liệu nhìn thấy trên game để cộng dồn.")

# === KHU VỰC 2: THỐNG KÊ (QUAN TRỌNG NHẤT) ===
st.divider()

if len(st.session_state.history) > 0 or (st.session_state.init_tai + st.session_state.init_xiu > 0):
    
    # 2.1 TÍNH TOÁN DỮ LIỆU
    sl_tai_moi = len([x for x in st.session_state.history if x['ket_qua'] == 'Tài'])
    sl_xiu_moi = len([x for x in st.session_state.history if x['ket_qua'] == 'Xỉu'])
    
    tong_tai = st.session_state.init_tai + sl_tai_moi
    tong_xiu = st.session_state.init_xiu + sl_xiu_moi
    tong_cong = tong_tai + tong_xiu
    
    # 2.2 HIỂN THỊ TỔNG QUAN (4 Cột)
    st.subheader("📈 CHỈ SỐ TỔNG QUAN")
    m1, m2, m3, m4 = st.columns(4)
    
    m1.metric("Tổng Số Ván", tong_cong, border=True)
    
    if tong_cong > 0:
        pct_tai = (tong_tai / tong_cong) * 100
        pct_xiu = (tong_xiu / tong_cong) * 100
        delta_tai = f"{pct_tai:.1f}%"
        delta_xiu = f"{pct_xiu:.1f}%"
    else:
        delta_tai = delta_xiu = "0%"
        
    m2.metric("🔴 TỔNG TÀI", tong_tai, delta=delta_tai, border=True)
    m3.metric("🔵 TỔNG XỈU", tong_xiu, delta=delta_xiu, border=True)
    
    # Logic Xu Hướng
    if tong_tai > tong_xiu: xu_huong = "Cầu đang nghiêng TÀI"
    elif tong_xiu > tong_tai: xu_huong = "Cầu đang nghiêng XỈU"
    else: xu_huong = "Cầu đang CÂN BẰNG"
    m4.info(f"**{xu_huong}**")

    # 2.3 PHÂN TÍCH CẦU (BỆT & NHẢY) - YÊU CẦU CHÍNH
    if len(st.session_state.history) > 0:
        bet, max_bet, nhay, max_nhay = phan_tich_cau_chi_tiet(st.session_state.history)
        
        st.write("")
        st.subheader("⚡ PHÂN TÍCH NHỊP CẦU (BỆT vs NHẢY)")
        
        # Giao diện 2 cột lớn cho 2 loại cầu
        col_bet, col_nhay = st.columns(2)
        
        with col_bet:
            st.error("🐍 THỐNG KÊ CẦU BỆT (Dây)", icon="🔥")
            c_b1, c_b2 = st.columns(2)
            c_b1.metric("Tổng Số Dây Bệt", bet)
            c_b2.metric("Bệt Dài Nhất", f"{max_bet} ván")
            st.caption("*(Là dây có từ 2 ván cùng màu liên tiếp trở lên)*")
            
        with col_nhay:
            st.info("🐰 THỐNG KÊ CẦU NHẢY (1-1)", icon="⚡")
            c_n1, c_n2 = st.columns(2)
            c_n1.metric("Tổng Số Dây Nhảy", nhay)
            c_n2.metric("Nhảy Dài Nhất", f"{max_nhay} nhịp")
            st.caption("*(Là dây thay đổi Tài-Xỉu liên tiếp từ 3 nhịp trở lên)*")

    # 2.4 VISUAL ROADMAP (Lịch sử dạng hình ảnh)
    st.write("")
    st.subheader("📜 LỊCH SỬ NHẬP LIỆU")
    
    # Hiển thị đẹp hơn dạng chuỗi icon
    road_map = []
    for h in st.session_state.history:
        val = str(h['diem']) if h['diem'] and h['diem'] > 0 else ""
        if h['ket_qua'] == 'Tài':
            road_map.append(f"<span class='tai-text'>🔴{val}</span>")
        else:
            road_map.append(f"<span class='xiu-text'>🔵{val}</span>")
    
    # Cho vào container cuộn ngang
    html_map = " &nbsp; ➜ &nbsp; ".join(road_map)
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; overflow-x: auto; white-space: nowrap; font-size: 20px;">
        {html_map}
    </div>
    """, unsafe_allow_html=True)
    
    # Nút Sửa Lỗi nằm gọn bên dưới
    with st.expander("🛠️ Sửa / Xóa Ván Nhập Sai"):
        if st.button("↩️ Undo (Xóa ván cuối)"):
            st.session_state.history.pop()
            st.rerun()

else:
    st.warning("👈 Hãy nhập dữ liệu ván đầu tiên hoặc cài đặt tổng số ban đầu.")
