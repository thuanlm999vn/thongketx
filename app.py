import streamlit as st
import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Tai Xiu Stats Master", page_icon="📊", layout="centered")

# --- CSS GIAO DIỆN ---
st.markdown("""
    <style>
    /* Nền tối */
    .stApp { background-color: #0e1117; color: white; }
    
    /* Box Thống Kê */
    .stat-card {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-val { font-size: 24px; font-weight: bold; color: #fff; }
    .stat-lbl { font-size: 12px; color: #9ca3af; text-transform: uppercase; margin-top: 5px;}
    
    /* Nút bấm Tài/Xỉu */
    .stButton>button {
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
        border: none;
    }
    
    /* Lịch sử Visual */
    .dot {
        display: inline-block;
        width: 28px; height: 28px;
        line-height: 28px;
        text-align: center;
        border-radius: 50%;
        font-size: 11px; font-weight: bold;
        margin: 2px;
    }
    .bg-tai { background-color: #ef4444; color: white; }
    .bg-xiu { background-color: #3b82f6; color: white; }
    
    /* Ẩn phần thừa */
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- LOGIC ---
def add_result(res):
    st.session_state.history.insert(0, {'result': res, 'ts': datetime.datetime.now()})
    st.session_state.history = st.session_state.history[:200]

def phan_tich_so_lieu(history):
    if not history: return None
    
    total = len(history)
    tai = len([x for x in history if x['result'] == 'Tài'])
    xiu = len([x for x in history if x['result'] == 'Xỉu'])
    
    # --- TÍNH MAX BỆT & MAX NHẢY ---
    # Duyệt toàn bộ lịch sử để tìm dây dài nhất
    max_bet = 0
    max_nhay = 0
    
    # Biến tạm
    curr_bet = 1
    curr_nhay = 1
    
    # Duyệt ngược từ quá khứ (cuối mảng) về hiện tại (đầu mảng)
    # history[0] là mới nhất. history[-1] là cũ nhất.
    # Đảo ngược list để duyệt theo dòng thời gian
    hist_rev = history[::-1]
    
    if total > 0:
        # Khởi tạo max ít nhất là 1 nếu có dữ liệu
        max_bet = 1
        max_nhay = 1
        
    for i in range(1, total):
        prev = hist_rev[i-1]['result']
        curr = hist_rev[i]['result']
        
        # Tính Bệt (Giống nhau)
        if curr == prev:
            curr_bet += 1
        else:
            max_bet = max(max_bet, curr_bet)
            curr_bet = 1
            
        # Tính Nhảy (Khác nhau)
        if curr != prev:
            curr_nhay += 1
        else:
            max_nhay = max(max_nhay, curr_nhay)
            curr_nhay = 1
            
    # Check lần cuối sau khi hết vòng lặp
    max_bet = max(max_bet, curr_bet)
    max_nhay = max(max_nhay, curr_nhay)

    return {
        'total': total,
        'tai': tai,
        'xiu': xiu,
        'tai_pct': int(tai/total*100),
        'xiu_pct': int(xiu/total*100),
        'max_bet': max_bet,
        'max_nhay': max_nhay
    }

def du_doan_ket_qua(history):
    # Logic dự đoán đơn giản dựa trên cầu
    if not history: return "...", "Chưa có dữ liệu"
    
    # Tính cầu hiện tại
    current_streak = 1
    last_res = history[0]['result']
    for i in range(1, len(history)):
        if history[i]['result'] == last_res:
            current_streak += 1
        else:
            break
            
    pred = ""
    reason = ""
    
    if current_streak >= 5:
        pred = "Xỉu" if last_res == "Tài" else "Tài"
        reason = f"Bẻ cầu bệt (đang bệt {current_streak})"
    elif current_streak == 1:
        # Vừa đổi màu, kiểm tra xem có đang đi dây 1-1 dài không
        # (Logic đơn giản: Nếu trước đó nhảy nhiều thì bệt, không thì theo 1-1)
        pred = "Xỉu" if last_res == "Tài" else "Tài"
        reason = "Bắt theo cầu Nhảy (1-1)"
    else:
        pred = last_res
        reason = f"Theo cầu Bệt (đang {current_streak})"
        
    return pred, reason

# --- GIAO DIỆN CHÍNH ---
c1, c2 = st.columns([4,1])
with c1: st.title("📊 THỐNG KÊ TÀI XỈU")
with c2: 
    if st.button("🗑️"):
        st.session_state.history = []
        st.rerun()

data = phan_tich_so_lieu(st.session_state.history)

if data:
    # 1. HÀNG THỐNG KÊ QUAN TRỌNG (MAX BỆT / NHẢY)
    st.caption("🏆 KỶ LỤC CẦU (Toàn lịch sử)")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="stat-card" style="border-color:#eab308"><div class="stat-val" style="color:#facc15">{data['max_bet']}</div><div class="stat-lbl">Max Bệt</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="stat-card" style="border-color:#22c55e"><div class="stat-val" style="color:#4ade80">{data['max_nhay']}</div><div class="stat-lbl">Max Nhảy</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="stat-card"><div class="stat-val text-red-400" style="color:#f87171">{data['tai']}</div><div class="stat-lbl">Tổng Tài</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="stat-card"><div class="stat-val text-blue-400" style="color:#60a5fa">{data['xiu']}</div><div class="stat-lbl">Tổng Xỉu</div></div>""", unsafe_allow_html=True)

    # 2. KHU VỰC NHẬP LIỆU
    st.write("")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔴 TÀI", use_container_width=True, type="primary"):
            add_result("Tài")
            st.rerun()
    with b2:
        if st.button("🔵 XỈU", use_container_width=True, type="primary"):
            add_result("Xỉu")
            st.rerun()

    # Nhập chuỗi
    with st.expander("⌨️ Nhập chuỗi số"):
        txt = st.text_input("VD: 12 4 10 (Mới nhất bên trái)")
        if st.button("Lưu"):
            nums = [int(s) for s in txt.split() if s.isdigit()]
            for n in nums[::-1]:
                res = 'Tài' if 11 <= n <= 18 else ('Xỉu' if 3 <= n <= 10 else None)
                if res: add_result(res)
            st.rerun()

    # 3. NÚT DỰ ĐOÁN (ON DEMAND)
    st.write("")
    col_btn, col_res = st.columns([1, 2])
    with col_btn:
        show_pred = st.button("🔮 Dự đoán ván tiếp")
    
    with col_res:
        if show_pred:
            pred_val, reason = du_doan_ket_qua(st.session_state.history)
            color = "#ef4444" if pred_val == "Tài" else "#3b82f6"
            st.markdown(f"""
            <div style="border: 1px solid {color}; padding: 10px; border-radius: 8px; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: space-between;">
                <span style="color: #9ca3af; font-size: 14px;">Gợi ý:</span>
                <span style="font-weight: 900; font-size: 24px; color: {color}; margin: 0 15px;">{pred_val.upper()}</span>
                <span style="font-size: 12px; color: #d1d5db; font-style: italic;">({reason})</span>
            </div>
            """, unsafe_allow_html=True)

    # 4. LỊCH SỬ
    st.markdown("---")
    html = '<div style="overflow-x: auto; white-space: nowrap; padding: 5px;">'
    for item in st.session_state.history:
        cls = "bg-tai" if item['result'] == "Tài" else "bg-xiu"
        txt = "T" if item['result'] == "Tài" else "X"
        html += f'<span class="dot {cls}">{txt}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)
    
    # Nút Undo
    if st.button("↩️ Xóa ván cuối"):
        st.session_state.history.pop(0)
        st.rerun()

else:
    st.info("👈 Mời nhập ván đầu tiên")
    # Nút ảo để hiện giao diện nhập cho lần đầu
    b1, b2 = st.columns(2)
    with b1:
        if st.button("🔴 TÀI", use_container_width=True, type="primary"):
            add_result("Tài")
            st.rerun()
    with b2:
        if st.button("🔵 XỈU", use_container_width=True, type="primary"):
            add_result("Xỉu")
            st.rerun()
