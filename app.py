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

# --- KHỞI TẠO AI ---
@st.cache_resource
def load_ai_reader():
    return easyocr.Reader(['en'], gpu=False)

# --- HÀM XỬ LÝ ẢNH THÔNG MINH (THEO CỘT) ---
def doc_so_tu_anh(uploaded_file):
    try:
        # 1. Đọc và Tiền xử lý ảnh
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        
        # Chuyển xám và tăng tương phản để tách số khỏi nền
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # 2. AI Đọc (Lấy cả tọa độ)
        reader = load_ai_reader()
        # detail=1 để lấy tọa độ khung (bounding box)
        raw_results = reader.readtext(thresh, detail=1, allowlist='0123456789')
        
        # 3. Thuật toán sắp xếp: CỘT TRƯỚC -> HÀNG SAU
        # raw_results có dạng: [ [box, text, conf], ... ]
        # box = [[tl, tr, br, bl]]
        
        detected_items = []
        for (bbox, text, prob) in raw_results:
            # Lọc số rác
            if not text.isdigit(): continue
            num = int(text)
            if not (3 <= num <= 18): continue
            
            # Tính tọa độ trung tâm của con số (Center X, Center Y)
            (tl, tr, br, bl) = bbox
            center_x = int((tl[0] + tr[0]) / 2)
            center_y = int((tl[1] + bl[1]) / 2)
            
            detected_items.append({'val': num, 'cx': center_x, 'cy': center_y})

        if not detected_items:
            return []

        # --- LOGIC SẮP XẾP CỘT ---
        # B1: Sắp xếp tất cả theo tọa độ X (để gom các số cùng cột lại gần nhau)
        detected_items.sort(key=lambda k: k['cx'])

        sorted_results = []
        current_column = []
        
        if len(detected_items) > 0:
            current_column.append(detected_items[0])
            
            # B2: Duyệt qua danh sách, nếu X lệch ít (< 30px) thì coi là cùng cột
            # Nếu X lệch nhiều -> Qua cột mới
            THRESHOLD_X = 30 # Độ lệch cho phép (pixel)
            
            for i in range(1, len(detected_items)):
                diff = abs(detected_items[i]['cx'] - detected_items[i-1]['cx'])
                
                if diff < THRESHOLD_X:
                    # Vẫn là cột cũ
                    current_column.append(detected_items[i])
                else:
                    # Sang cột mới -> Sắp xếp cột cũ theo Y (Trên xuống dưới) rồi lưu lại
                    current_column.sort(key=lambda k: k['cy'])
                    sorted_results.extend([item['val'] for item in current_column])
                    # Reset cột mới
                    current_column = [detected_items[i]]
            
            # Lưu cột cuối cùng
            current_column.sort(key=lambda k: k['cy'])
            sorted_results.extend([item['val'] for item in current_column])

        return sorted_results

    except Exception as e:
        st.error(f"Lỗi xử lý: {e}")
        return []

# --- KHỞI TẠO DỮ LIỆU ---
if 'history' not in st.session_state:
    st.session_state.history = []

def them_ket_qua(diem=None, ket_qua=None):
    if diem is not None:
        if diem > 0: 
            if 11 <= diem <= 18: ket_qua = 'Tài'
            elif 3 <= diem <= 10: ket_qua = 'Xỉu'
    st.session_state.history.append({'diem': diem, 'ket_qua': ket_qua})

def phan_tich_cau(data):
    if not data: return 0, 0, 0, 0
    results = [x['ket_qua'] for x in data]
    
    # Bệt
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

    # Nhảy
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

# --- GIAO DIỆN ---
st.title("🎲 SUPER SOI CẦU AI (Cột Dọc)")

# === UPLOAD ẢNH ===
with st.expander("📸 QUÉT ẢNH TỰ ĐỘNG", expanded=True):
    uploaded_file = st.file_uploader("Chọn ảnh (Cắt gọn khung điểm số):", type=['jpg', 'png', 'jpeg'])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Ảnh đầu vào", use_container_width=True)
        
        if st.button("🚀 QUÉT SỐ THEO CỘT DỌC", type="primary"):
            with st.spinner("AI đang đọc theo thứ tự Cột Dọc..."):
                uploaded_file.seek(0)
                ket_qua_so = doc_so_tu_anh(uploaded_file)
                
                if len(ket_qua_so) > 0:
                    st.success(f"✅ Tìm thấy {len(ket_qua_so)} số (Thứ tự cột): {ket_qua_so}")
                    st.session_state.temp_scan = ket_qua_so
                else:
                    st.warning("⚠️ Không tìm thấy số hợp lệ (3-18). Hãy cắt ảnh sát vào bảng số!")

    if 'temp_scan' in st.session_state and len(st.session_state.temp_scan) > 0:
        if st.button("📥 Nạp dữ liệu này vào"):
            st.session_state.history = [] 
            for so in st.session_state.temp_scan:
                them_ket_qua(diem=so)
            del st.session_state.temp_scan
            st.rerun()

# === NHẬP LIỆU THỦ CÔNG ===
st.divider()
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
    with st.popover("🔢 Số"):
        num = st.number_input("Điểm:", 3, 18, step=1)
        if st.button("Lưu"):
            them_ket_qua(diem=int(num))
            st.rerun()

# === SỬA LỖI ===
if len(st.session_state.history) > 0:
    with st.expander("🛠️ SỬA / XÓA"):
        if st.button("↩️ Undo"):
            st.session_state.history.pop()
            st.rerun()
        
        so_luong = len(st.session_state.history)
        start = max(0, so_luong - 5)
        with st.form("sua"):
            for i in range(so_luong - 1, start - 1, -1):
                item = st.session_state.history[i]
                cc1, cc2, cc3 = st.columns([1, 2, 2])
                with cc1: st.write(f"#{i+1}")
                with cc2: 
                    idx = 0 if item['ket_qua'] == 'Tài' else 1
                    st.session_state[f"k_{i}"] = st.selectbox("", ["Tài", "Xỉu"], index=idx, key=f"s_{i}", label_visibility="collapsed")
                with cc3:
                    d_val = item['diem'] if item['diem'] else 0
                    st.session_state[f"d_{i}"] = st.number_input("", value=d_val, key=f"n_{i}", label_visibility="collapsed")
            if st.form_submit_button("Lưu"):
                for i in range(so_luong - 1, start - 1, -1):
                    st.session_state.history[i]['ket_qua'] = st.session_state[f"s_{i}"]
                    n_val = st.session_state[f"n_{i}"]
                    st.session_state.history[i]['diem'] = n_val if n_val > 0 else None
                st.rerun()

# === DASHBOARD ===
if len(st.session_state.history) > 0:
    st.divider()
    df = pd.DataFrame(st.session_state.history)
    tong = len(df)
    tai = len(df[df['ket_qua'] == 'Tài'])
    xiu = len(df[df['ket_qua'] == 'Xỉu'])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Tổng", tong)
    m2.metric("Tài 🔴", f"{tai}")
    m3.metric("Xỉu 🔵", f"{xiu}")
    
    bet, max_bet, nhay, max_nhay = phan_tich_cau(st.session_state.history)
    st.info(f"🐍 Bệt max: {max_bet} | ⚡ Nhảy max: {max_nhay}")
    
    icons = ["🔴" if h['ket_qua'] == 'Tài' else "🔵" for h in st.session_state.history]
    st.text_area("Log", " ".join(icons))
