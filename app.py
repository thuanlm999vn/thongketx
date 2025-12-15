import streamlit as st
import pandas as pd
import easyocr
import cv2
import numpy as np

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Soi Cầu AI Pro", page_icon="🎲", layout="centered")

# --- CSS GIAO DIỆN ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; font-weight: bold;}
    div[data-testid="stMetricValue"] { font-size: 24px; }
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO AI (CACHE ĐỂ CHẠY NHANH) ---
@st.cache_resource
def load_ai_reader():
    # Tải model nhận diện chữ (chạy trên CPU)
    return easyocr.Reader(['en'], gpu=False) 

# --- HÀM XỬ LÝ ẢNH ---
def doc_so_tu_anh(uploaded_file):
    try:
        # 1. Chuyển ảnh upload thành định dạng OpenCV
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        
        # 2. Dùng AI đọc số
        reader = load_ai_reader()
        # detail=0 chỉ lấy text
        results = reader.readtext(image, detail=0) 
        
        # 3. Lọc lấy các con số hợp lệ (3-18)
        so_tim_thay = []
        for text in results:
            # Loại bỏ ký tự lạ, chỉ lấy số
            text_clean = ''.join(filter(str.isdigit, text))
            if text_clean.isdigit():
                num = int(text_clean)
                # Chỉ lấy số trong khoảng điểm Tài Xỉu
                if 3 <= num <= 18:
                    so_tim_thay.append(num)
        
        return so_tim_thay
    except Exception as e:
        st.error(f"Lỗi đọc ảnh: {e}")
        return []

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
st.title("🎲 SUPER SOI CẦU AI")

# === PHẦN 1: AI ĐỌC ẢNH TỰ ĐỘNG ===
with st.expander("📸 QUÉT ẢNH TỰ ĐỘNG", expanded=True):
    uploaded_file = st.file_uploader("Chọn ảnh game:", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Ảnh đã chọn", use_container_width=True)
        
        if st.button("🚀 BẤM ĐỂ QUÉT SỐ TỪ ẢNH", type="primary"):
            with st.spinner("AI đang căng mắt đọc số... (Mất khoảng 5-10 giây)"):
                # Reset file pointer để đọc lại từ đầu
                uploaded_file.seek(0)
                ket_qua_so = doc_so_tu_anh(uploaded_file)
                
                if len(ket_qua_so) > 0:
                    st.success(f"✅ Đã tìm thấy {len(ket_qua_so)} con số: {ket_qua_so}")
                    # Hỏi người dùng có muốn nạp vào không
                    st.session_state.temp_scan = ket_qua_so
                else:
                    st.warning("⚠️ Không đọc được số nào rõ ràng. Hãy thử ảnh nét hơn hoặc nhập tay bên dưới.")

    # Nút xác nhận nạp dữ liệu
    if 'temp_scan' in st.session_state and len(st.session_state.temp_scan) > 0:
        if st.button("📥 Nạp các số này vào Thống Kê"):
            # Xóa dữ liệu cũ nếu muốn (hoặc nối tiếp)
            st.session_state.history = [] 
            for so in st.session_state.temp_scan:
                them_ket_qua(diem=so)
            del st.session_state.temp_scan # Xóa tạm
            st.rerun()

# === PHẦN NHẬP LIỆU ===
st.divider()
st.caption("👇 NHẬP KẾT QUẢ VÁN MỚI (THỦ CÔNG)")
c1, c2, c3 = st.columns([1, 1, 1])

with c1:
    if st.button("🔴 TÀI"):
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
