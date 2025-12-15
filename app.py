import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Tai Xiu Auto Tracker", page_icon="🎲", layout="wide")

# --- CSS GIAO DIỆN (DARK MODE PRO) ---
st.markdown("""
    <style>
    /* Nền tối chủ đạo */
    .stApp {
        background: linear-gradient(to bottom right, #111827, #1f2937, #111827);
        color: white;
    }
    
    /* Card Container */
    .css-card {
        background-color: rgba(31, 41, 55, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(75, 85, 99, 0.4);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Nút bấm Tài/Xỉu to */
    .stButton>button {
        border-radius: 12px;
        height: 60px;
        font-weight: bold;
        font-size: 20px;
        border: none;
        transition: all 0.2s;
    }
    
    /* Chỉ số thống kê */
    .stat-label { font-size: 13px; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-value { font-size: 32px; font-weight: 800; }
    
    /* Lịch sử cầu */
    .history-container {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
    }
    .history-item {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 40px;
        height: 40px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 14px;
        position: relative;
    }
    .his-tai { 
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); 
        color: white; 
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
    }
    .his-xiu { 
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
        color: white;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
    }
    
    /* Ẩn mặc định của Streamlit */
    .stDeployButton {display:none;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- HÀM LOGIC ---
def add_result(result, total=None):
    new_entry = {
        'id': datetime.datetime.now().timestamp(),
        'result': result,
        'total': total,
        'timestamp': datetime.datetime.now().strftime("%H:%M:%S")
    }
    # Thêm vào đầu danh sách (Mới nhất)
    st.session_state.history.insert(0, new_entry)
    # Giữ lại 200 kết quả
    st.session_state.history = st.session_state.history[:200]

def analyze_data(history):
    if not history:
        return None
    
    df = pd.DataFrame(history)
    total = len(df)
    tai_count = len(df[df['result'] == 'Tài'])
    xiu_count = len(df[df['result'] == 'Xỉu'])
    
    # --- THUẬT TOÁN ĐẾM BỆT/NHẢY (THEO ĐỊNH NGHĨA CỦA BẠN) ---
    # Duyệt từ quá khứ đến hiện tại để đếm tổng số lần chuyển đổi
    # history[0] là mới nhất, history[-1] là cũ nhất
    # Ta duyệt từ 0 đến len-1 để so sánh cặp (i) và (i+1)
    
    total_bet = 0  # Tổng số điểm Bệt
    total_nhay = 0 # Tổng số điểm Nhảy
    
    for i in range(len(history) - 1):
        current = history[i]['result']
        prev = history[i+1]['result'] # Ván trước đó
        
        if current == prev:
            total_bet += 1 # Cùng màu -> Bệt
        else:
            total_nhay += 1 # Khác màu -> Nhảy

    # --- TÍNH DÂY DÀI NHẤT (MAX STREAK) ---
    # Tính chuỗi liên tiếp hiện tại (Current Streak)
    current_streak = 1
    current_type = history[0]['result']
    for i in range(1, len(history)):
        if history[i]['result'] == current_type:
            current_streak += 1
        else:
            break
            
    # Tính Max Bệt (Dây cùng màu dài nhất) & Max Nhảy (Dây 1-1 dài nhất)
    max_bet_streak = 0
    max_nhay_streak = 0
    
    temp_bet = 1
    temp_nhay = 1
    
    # Đảo ngược để duyệt theo dòng thời gian (Cũ -> Mới)
    hist_reversed = history[::-1]
    
    for i in range(1, len(hist_reversed)):
        curr = hist_reversed[i]['result']
        prev = hist_reversed[i-1]['result']
        
        # Logic Max Bệt (Liên tiếp giống nhau)
        if curr == prev:
            temp_bet += 1
        else:
            max_bet_streak = max(max_bet_streak, temp_bet)
            temp_bet = 1
            
        # Logic Max Nhảy (Liên tiếp khác nhau: T-X-T-X)
        if curr != prev:
            temp_nhay += 1
        else:
            max_nhay_streak = max(max_nhay_streak, temp_nhay)
            temp_nhay = 1
            
    # Chốt sổ lần cuối
    max_bet_streak = max(max_bet_streak, temp_bet)
    max_nhay_streak = max(max_nhay_streak, temp_nhay)

    # --- DỰ ĐOÁN (PREDICTION) ---
    prediction_val = ''
    confidence = 0
    reason = ''
    
    # Đang bệt hay đang nhảy?
    is_beting = False
    is_nhaying = False
    
    if len(history) >= 2:
        if history[0]['result'] == history[1]['result']:
            is_beting = True
        else:
            is_nhaying = True
            
    # Logic Dự Đoán
    if current_streak >= 5:
        prediction_val = 'Xỉu' if current_type == 'Tài' else 'Tài'
        confidence = min(current_streak * 12, 85)
        reason = f"Đang bệt {current_type} {current_streak} ván, dễ gãy cầu"
        
    elif is_nhaying and current_streak == 1: 
        # Đang đi cầu 1-1 (Vừa đổi màu)
        # Kiểm tra xem dây nhảy này dài bao nhiêu rồi
        curr_nhay_len = 0
        for i in range(len(history)-1):
            if history[i]['result'] != history[i+1]['result']:
                curr_nhay_len += 1
            else:
                break
        
        if curr_nhay_len >= 4:
            prediction_val = history[0]['result'] # Bắt bệt lại (Gãy cầu nhảy)
            confidence = 60
            reason = f"Cầu nhảy dài {curr_nhay_len} nhịp, canh bắt Bệt"
        else:
            prediction_val = 'Xỉu' if history[0]['result'] == 'Tài' else 'Tài' # Bắt tiếp cầu nhảy
            confidence = 50
            reason = "Đang đi cầu 1-1 đẹp"
            
    elif total_bet > total_nhay * 1.5:
        prediction_val = 'Xỉu' if history[0]['result'] == 'Tài' else 'Tài'
        confidence = 55
        reason = f"Tổng Bệt quá nhiều ({total_bet}), xu hướng về Nhảy"
        
    else:
        # Mặc định theo cầu nghiêng
        if tai_count > xiu_count:
            prediction_val = 'Xỉu' # Cân bằng lại
            confidence = 45
            reason = "Tài đang nhiều hơn, nuôi Xỉu"
        else:
            prediction_val = 'Tài'
            confidence = 45
            reason = "Xỉu đang nhiều hơn, nuôi Tài"

    return {
        'total': total,
        'tai': tai_count,
        'xiu': xiu_count,
        'tai_pct': round(tai_count/total*100, 0) if total else 0,
        'xiu_pct': round(xiu_count/total*100, 0) if total else 0,
        'total_bet': total_bet,
        'total_nhay': total_nhay,
        'max_bet': max_bet_streak,
        'max_nhay': max_nhay_streak,
        'pred_val': prediction_val,
        'confidence': confidence,
        'reason': reason
    }

# --- GIAO DIỆN HEADER ---
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("## 🎲 TAI XIU AUTO TRACKER")
    st.caption("Thống kê Bệt/Nhảy chuẩn xác")
with col_h2:
    if st.button("🗑️ Xóa"):
        st.session_state.history = []
        st.rerun()

# --- KHU VỰC NHẬP LIỆU ---
st.markdown('<div class="css-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    if st.button("🔴 TÀI", key="btn_tai", use_container_width=True, type="primary"):
        add_result("Tài")
        st.rerun()
with c2:
    if st.button("🔵 XỈU", key="btn_xiu", use_container_width=True, type="primary"):
        add_result("Xỉu")
        st.rerun()

# Nhập nhanh
with st.expander("⌨️ Nhập nhanh chuỗi số"):
    quick_input = st.text_input("Dán chuỗi số vào đây (VD: 12 4 13...)", key="quick_in")
    if st.button("Thêm chuỗi"):
        if quick_input:
            nums = [int(s) for s in quick_input.split() if s.isdigit()]
            for n in nums:
                if 3 <= n <= 18:
                    res = 'Tài' if n >= 11 else 'Xỉu'
                    # Thêm ngược từ quá khứ (cuối chuỗi) -> hiện tại
                    # Nhưng logic add_result là thêm lên đầu, nên ta duyệt xuôi
                    # VD nhập: 12 (cũ) 13 (mới) -> add 12 trước, add 13 sau
                    new_entry = {
                        'id': datetime.datetime.now().timestamp() + n,
                        'result': res,
                        'total': n,
                        'timestamp': datetime.datetime.now().strftime("%H:%M:%S")
                    }
                    st.session_state.history.insert(0, new_entry)
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- PHÂN TÍCH & DỰ ĐOÁN ---
if st.session_state.history:
    data = analyze_data(st.session_state.history)
    
    # 1. CARD DỰ ĐOÁN (NỔI BẬT NHẤT)
    st.markdown(f"""
    <div class="css-card" style="border: 2px solid {'#ef4444' if data['pred_val'] == 'Tài' else '#3b82f6'}; text-align: center;">
        <div style="font-size: 14px; color: #9ca3af; margin-bottom: 5px;">DỰ ĐOÁN VÁN TIẾP THEO</div>
        <div style="font-size: 60px; font-weight: 900; line-height: 1; color: {'#ef4444' if data['pred_val'] == 'Tài' else '#3b82f6'};">
            {data['pred_val'].upper()}
        </div>
        <div style="font-size: 24px; font-weight: bold; color: #f472b6; margin-top: 10px;">
            {data['confidence']}%
        </div>
        <div style="color: #d1d5db; font-style: italic; margin-top: 5px;">
            "{data['reason']}"
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. THỐNG KÊ TỔNG QUAN
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        st.markdown(f"""
        <div class="css-card" style="text-align:center">
            <div class="stat-label">TỔNG VÁN</div>
            <div class="stat-value">{data['total']}</div>
        </div>""", unsafe_allow_html=True)
    with c_s2:
        st.markdown(f"""
        <div class="css-card" style="text-align:center; border-bottom: 4px solid #ef4444;">
            <div class="stat-label">TÀI</div>
            <div class="stat-value" style="color:#f87171">{data['tai']}</div>
            <div style="font-size:12px; color:#fca5a5">{data['tai_pct']}%</div>
        </div>""", unsafe_allow_html=True)
    with c_s3:
        st.markdown(f"""
        <div class="css-card" style="text-align:center; border-bottom: 4px solid #3b82f6;">
            <div class="stat-label">XỈU</div>
            <div class="stat-value" style="color:#60a5fa">{data['xiu']}</div>
            <div style="font-size:12px; color:#93c5fd">{data['xiu_pct']}%</div>
        </div>""", unsafe_allow_html=True)

    # 3. THỐNG KÊ BỆT / NHẢY (THEO YÊU CẦU CỦA BẠN)
    col_pat1, col_pat2 = st.columns(2)
    
    # Card BỆT
    with col_pat1:
        st.markdown(f"""
        <div class="css-card">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
                <div style="font-size:24px;">🔥</div>
                <div style="font-weight:bold; color:#fbbf24; font-size:18px;">CẦU BỆT (Dây)</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:end;">
                <div>
                    <div class="stat-label">TỔNG ĐIỂM BỆT</div>
                    <div class="stat-value" style="color:#fbbf24">{data['total_bet']}</div>
                </div>
                <div style="text-align:right;">
                    <div class="stat-label">DÂY DÀI NHẤT</div>
                    <div style="font-size:24px; font-weight:bold; color:#fff">{data['max_bet']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Card NHẢY
    with col_pat2:
        st.markdown(f"""
        <div class="css-card">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:15px;">
                <div style="font-size:24px;">⚡</div>
                <div style="font-weight:bold; color:#34d399; font-size:18px;">CẦU NHẢY (1-1)</div>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:end;">
                <div>
                    <div class="stat-label">TỔNG ĐIỂM NHẢY</div>
                    <div class="stat-value" style="color:#34d399">{data['total_nhay']}</div>
                </div>
                <div style="text-align:right;">
                    <div class="stat-label">NHẢY DÀI NHẤT</div>
                    <div style="font-size:24px; font-weight:bold; color:#fff">{data['max_nhay']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4. BIỂU ĐỒ & LỊCH SỬ
    c_chart, c_hist = st.columns([1, 2])
    
    with c_chart:
        # Biểu đồ tròn Bệt vs Nhảy
        fig = px.pie(names=['Bệt', 'Nhảy'], values=[data['total_bet'], data['total_nhay']],
                     color=['Bệt', 'Nhảy'], 
                     color_discrete_map={'Bệt':'#f59e0b', 'Nhảy':'#10b981'},
                     hole=0.6)
        fig.update_layout(
            showlegend=False, 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=0, b=0, l=0, r=0),
            height=200,
            annotations=[dict(text=f"{data['total_bet']}/{data['total_nhay']}", x=0.5, y=0.5, font_size=20, showarrow=False, font_color='white')]
        )
        st.markdown('<div class="css-card" style="height: 240px; display:flex; align-items:center; justify-content:center;">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c_hist:
        # Lịch sử dạng Visual
        hist_html = ""
        for item in st.session_state.history[:48]: # 48 ván gần nhất
            cls = "his-tai" if item['result'] == 'Tài' else "his-xiu"
            val = str(item['total']) if item['total'] else ("T" if item['result'] == 'Tài' else "X")
            hist_html += f'<div class="history-item {cls}">{val}</div>'
            
        st.markdown(f"""
        <div class="css-card" style="height: 240px; overflow-y: auto;">
            <div class="stat-label" style="margin-bottom:10px;">LỊCH SỬ GẦN NHẤT</div>
            <div class="history-container">
                {hist_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("👈 Bắt đầu bằng cách nhập TÀI hoặc XỈU")
