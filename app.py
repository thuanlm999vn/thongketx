import streamlit as st
import pandas as pd
import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Tai Xiu AI Predictor", page_icon="🎯", layout="centered")

# --- CSS GIAO DIỆN CAO CẤP ---
st.markdown("""
    <style>
    /* Nền tổng thể */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* CARD DỰ ĐOÁN (QUAN TRỌNG NHẤT) */
    .prediction-card {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 2px solid rgba(255,255,255,0.1);
    }
    .pred-tai {
        background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);
        border-color: #ef4444;
    }
    .pred-xiu {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%);
        border-color: #3b82f6;
    }
    .pred-wait {
        background: #1f2937;
        border-color: #4b5563;
    }
    
    /* Typography */
    .big-text { font-size: 50px; font-weight: 900; letter-spacing: 2px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    .sub-text { font-size: 18px; color: #e5e7eb; margin-top: 5px; font-weight: 500;}
    .confidence-badge { 
        background-color: rgba(0,0,0,0.3); 
        padding: 5px 15px; 
        border-radius: 20px; 
        font-size: 14px; 
        display: inline-block;
        margin-top: 10px;
    }

    /* CARD THỐNG KÊ NHỎ */
    .stat-box {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #374151;
    }
    .stat-num { font-size: 24px; font-weight: bold; }
    .stat-label { font-size: 12px; color: #9ca3af; text-transform: uppercase; }
    
    /* HISTORY VISUAL */
    .history-dot {
        display: inline-block;
        width: 30px; 
        height: 30px; 
        line-height: 30px;
        text-align: center;
        border-radius: 50%;
        margin: 2px;
        font-weight: bold;
        font-size: 12px;
    }
    .dot-tai { background-color: #ef4444; color: white; }
    .dot-xiu { background-color: #3b82f6; color: white; }
    
    /* Ẩn các phần thừa của Streamlit */
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
    st.session_state.history = st.session_state.history[:100]

def phan_tich_va_du_doan(history):
    if not history: return None
    
    # 1. Thống kê cơ bản
    total = len(history)
    tai = len([x for x in history if x['result'] == 'Tài'])
    xiu = len([x for x in history if x['result'] == 'Xỉu'])
    
    # 2. Đếm Bệt/Nhảy Tổng quát
    # Duyệt từ quá khứ đến hiện tại để đếm cặp
    count_bet = 0
    count_nhay = 0
    hist_rev = history[::-1] # Đảo ngược để duyệt cũ -> mới
    for i in range(len(hist_rev)-1):
        if hist_rev[i]['result'] == hist_rev[i+1]['result']:
            count_bet += 1
        else:
            count_nhay += 1

    # 3. Phân tích Cầu Hiện Tại (Quan trọng nhất để dự đoán)
    # Lấy chuỗi giống nhau liên tiếp từ ván mới nhất
    current_streak = 1
    last_res = history[0]['result']
    for i in range(1, len(history)):
        if history[i]['result'] == last_res:
            current_streak += 1
        else:
            break
            
    # Lấy chuỗi 1-1 liên tiếp (Nhảy)
    # Ví dụ: T-X-T-X (streak = 4)
    current_switch_streak = 0
    if len(history) >= 2 and history[0]['result'] != history[1]['result']:
        # Đang ở trạng thái nhảy
        current_switch_streak = 1 # Đã nhảy 1 nhịp (cặp mới nhất)
        for i in range(1, len(history)-1):
            if history[i]['result'] != history[i+1]['result']:
                current_switch_streak += 1
            else:
                break
    
    # --- THUẬT TOÁN DỰ ĐOÁN ---
    # Logic: Bắt bẻ cầu khi dây quá dài
    pred = ""
    conf = 0
    reason = ""
    
    if current_streak >= 5:
        # Đang Bệt dài >= 5 -> Dự đoán Bẻ (Gãy)
        pred = "Xỉu" if last_res == "Tài" else "Tài"
        conf = 85
        reason = f"Đang Bệt {last_res} {current_streak} tay. Nguy cơ gãy cao!"
        
    elif current_streak >= 3:
        # Đang Bệt 3-4 -> Thường theo tiếp Bệt (Nuôi cầu)
        pred = last_res
        conf = 65
        reason = f"Cầu đang chạy Bệt {current_streak}. Theo cầu."
        
    elif current_switch_streak >= 4:
        # Đang Nhảy dài >= 4 nhịp (T-X-T-X) -> Dự đoán Bắt Bệt lại
        # Ván vừa rồi là A, thì ván này B, dự đoán ván sau là B (Bệt lại)
        # Nhưng đây là dự đoán kết quả ván tới. 
        # Nếu chuỗi 1-1 dài, thường nó sẽ gãy về Bệt.
        # Ván mới nhất là A. Theo quy luật 1-1 thì ván tới là B.
        # Nhưng nếu bẻ cầu 1-1 thì ván tới là A.
        pred = last_res 
        conf = 60
        reason = f"Cầu 1-1 đã chạy {current_switch_streak} nhịp. Canh bắt Bệt."
        
    else:
        # Không có cầu rõ ràng -> Dựa vào xác suất bù trừ
        if count_bet > count_nhay * 1.5:
            # Bệt nhiều quá -> Dự Nhảy
            pred = "Xỉu" if last_res == "Tài" else "Tài"
            conf = 55
            reason = "Tổng Bệt áp đảo, xu hướng trả Nhảy."
        elif tai > xiu + 2:
            pred = "Xỉu"
            conf = 50
            reason = "Tài đang nhiều hơn Xỉu, nuôi cân cửa."
        elif xiu > tai + 2:
            pred = "Tài"
            conf = 50
            reason = "Xỉu đang nhiều hơn Tài, nuôi cân cửa."
        else:
            pred = "..."
            reason = "Chờ thêm dữ liệu"

    return {
        'total': total, 'tai': tai, 'xiu': xiu,
        'bet': count_bet, 'nhay': count_nhay,
        'pred': pred, 'conf': conf, 'reason': reason
    }

# --- HEADER ---
c_h1, c_h2 = st.columns([5, 1])
with c_h1:
    st.markdown("### 🎯 AI SOI CẦU PRO")
with c_h2:
    if st.button("🗑️ Reset"):
        st.session_state.history = []
        st.rerun()

# --- MAIN ANALYSIS & PREDICTION ---
data = phan_tich_va_du_doan(st.session_state.history)

if data and data['pred'] != "...":
    # Xác định màu sắc Card dựa trên dự đoán
    card_class = "pred-tai" if data['pred'] == "Tài" else "pred-xiu"
    
    st.markdown(f"""
    <div class="prediction-card {card_class}">
        <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">🤖 AI DỰ ĐOÁN VÁN TIẾP THEO</div>
        <div class="big-text">{data['pred'].upper()}</div>
        <div class="sub-text">{data['reason']}</div>
        <div class="confidence-badge">⚡ Độ tin cậy: {data['conf']}%</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="prediction-card pred-wait">
        <div style="font-size: 40px;">⏳</div>
        <div class="sub-text">Đang chờ nhập dữ liệu...</div>
    </div>
    """, unsafe_allow_html=True)

# --- INPUT BUTTONS ---
c1, c2 = st.columns(2)
with c1:
    if st.button("🔴 TÀI", use_container_width=True, type="primary"):
        add_result("Tài")
        st.rerun()
with c2:
    if st.button("🔵 XỈU", use_container_width=True, type="primary"):
        add_result("Xỉu")
        st.rerun()
        
# Nhập nhanh
with st.expander("⌨️ Nhập chuỗi số"):
    txt = st.text_input("VD: 12 4 10 (Mới nhất bên trái)", label_visibility="collapsed")
    if st.button("Nạp chuỗi"):
        nums = [int(s) for s in txt.split() if s.isdigit()]
        # Duyệt ngược để nạp đúng thứ tự thời gian (Số cuối cùng nhập trước)
        for n in nums[::-1]:
            res = 'Tài' if 11 <= n <= 18 else ('Xỉu' if 3 <= n <= 10 else None)
            if res: add_result(res)
        st.rerun()

# --- STATS GRID ---
if data:
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"""<div class="stat-box"><div class="stat-num">{data['total']}</div><div class="stat-label">Tổng ván</div></div>""", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"""<div class="stat-box" style="border-color:#ef4444"><div class="stat-num" style="color:#f87171">{data['tai']}</div><div class="stat-label">Tài</div></div>""", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"""<div class="stat-box" style="border-color:#3b82f6"><div class="stat-num" style="color:#60a5fa">{data['xiu']}</div><div class="stat-label">Xỉu</div></div>""", unsafe_allow_html=True)
    with cols[3]:
        # Tỷ lệ Bệt/Nhảy
        ratio = f"{data['bet']}/{data['nhay']}"
        st.markdown(f"""<div class="stat-box"><div class="stat-num text-yellow-400" style="color:#fbbf24">{ratio}</div><div class="stat-label">Bệt / Nhảy</div></div>""", unsafe_allow_html=True)

# --- HISTORY VISUAL ---
if st.session_state.history:
    st.markdown("---")
    st.caption("📜 Lịch sử (Trái: Mới nhất ➜ Phải: Cũ nhất)")
    
    html = '<div style="overflow-x: auto; white-space: nowrap; padding-bottom: 10px;">'
    for item in st.session_state.history:
        cls = "dot-tai" if item['result'] == "Tài" else "dot-xiu"
        txt = "T" if item['result'] == "Tài" else "X"
        html += f'<span class="history-dot {cls}">{txt}</span>'
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Nút Undo
    if st.button("↩️ Xóa ván vừa nhập"):
        st.session_state.history.pop(0)
        st.rerun()
