import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import secrets
import os
from datetime import datetime, timedelta
# --- KHỞI TẠO CÁC BIẾN QUAN TRỌNG (Dán ngay đầu file, sau Import) ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # Tạo danh sách tin nhắn rỗng nếu chưa có
if "chat_session" not in st.session_state:
    try: 
        current_date = datetime.now().strftime("%A, ngày 25/11/2025") 
        lenh_cai_dat = f"""
        ... (giữ nguyên toàn bộ nội dung lệnh cài đặt) ...
        """
        
        # Sửa lại: Định nghĩa cấu hình bằng Dictionary (Plain Dict)
        config_search = {
            "tools": [{'googleSearch': {}}]
        }

        # Sửa lại dòng này
        model = genai.GenerativeModel(
    'models/gemini-2.5-pro', # <--- Tên model mới
    system_instruction=lenh_cai_dat,
    )
        
        st.session_state.chat_session = model.start_chat(history=[]) 
        st.session_state.config_search = config_search 
        
    except Exception as e:
        st.error(f"⚠️ Lỗi cấu hình API: Vui lòng kiểm tra lại Key hoặc kết nối mạng. Chi tiết: {e}")
        st.stop()
# --- CẤU HÌNH ADMIN ---
FILE_DATA = "key_data.json"
SDT_ADMIN = "0376274345"
ADMIN_PASSWORD = "levudepzai" 

# --- HÀM XỬ LÝ DATA ---
def load_data():
    if not os.path.exists(FILE_DATA):
        with open(FILE_DATA, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    try:
        with open(FILE_DATA, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(FILE_DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# [CẬP NHẬT] Hàm tạo key nhận thêm số ngày sử dụng
def tao_key_moi(sdt_khach, ghi_chu, so_ngay_dung):
    data = load_data()
    phan_duoi = secrets.token_hex(4).upper() 
    new_key = f"KEY-{phan_duoi[:4]}-{phan_duoi[4:]}"
    
    # Tính ngày hết hạn
    ngay_hien_tai = datetime.now()
    ngay_het_han = ngay_hien_tai + timedelta(days=so_ngay_dung)
    
    data[new_key] = {
        "status": "active",
        "sdt": sdt_khach,
        "created_at": ngay_hien_tai.strftime("%Y-%m-%d %H:%M"),
        "expiry_date": ngay_het_han.strftime("%Y-%m-%d %H:%M"), # Lưu ngày hết hạn
        "note": ghi_chu
    }
    save_data(data)
    return new_key, ngay_het_han.strftime("%d/%m/%Y")

# [CẬP NHẬT] Hàm check đăng nhập kiểm tra hạn sử dụng
def kiem_tra_dang_nhap(input_key, input_sdt):
    # 1. Admin
    if input_key == ADMIN_PASSWORD:
        return True, "admin", "Chào Sếp Vũ!"
    
    # 2. Khách
    data = load_data()
    if input_key in data:
        thong_tin = data[input_key]
        
        # Check SĐT
        if thong_tin.get("sdt") != input_sdt:
            return False, None, "❌ Sai số điện thoại đăng ký!"
        
        # Check Hạn sử dụng
        han_su_dung_str = thong_tin.get("expiry_date")
        if han_su_dung_str:
            han_su_dung = datetime.strptime(han_su_dung_str, "%Y-%m-%d %H:%M")
            if datetime.now() > han_su_dung:
                return False, None, "⚠️ Key đã HẾT HẠN! Vui lòng liên hệ Admin để gia hạn."
        
        # Nếu OK hết
        con_lai = ""
        if han_su_dung_str:
             han_su_dung = datetime.strptime(han_su_dung_str, "%Y-%m-%d %H:%M")
             so_ngay_con = (han_su_dung - datetime.now()).days
             con_lai = f"(Còn {so_ngay_con} ngày)"

        return True, "user", f"Xin chào {input_sdt}! {con_lai}"
            
    return False, None, "❌ Key không tồn tại!"


st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg"); 
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); z-index: -1; pointer-events: none;
    }
    .title-container { text-align: center; margin-bottom: 30px; margin-top: -20px; }
    .main-title { font-size: 2.5rem; font-weight: 800; color: white; text-shadow: 0 0 15px rgba(255,255,255,0.4); }
    .sub-title { font-size: 1rem; color: rgba(255,255,255,0.8); letter-spacing: 1px; }


    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

            /* --- VIỀN NEON 7 MÀU CHẠY (MỎNG NHƯNG TỎA SÁNG MẠNH) --- */
    
    /* LỚP 1: SỢI DÂY NGUỒN (Nét căng, chạy màu) */
    body::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 9999;
        pointer-events: none;
        
        padding: 4px; /* ĐỘ DÀY VIỀN CHỈ 4PX THÔI */
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: spin 4s linear infinite;
        
        /* Mask để đục thủng giữa */
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    
    /* LỚP 2: ÁNH SÁNG TỎA RA (GLOW) */
    body::after {
        content: "";
        position: fixed;
        /* Phủ trùm lên viền chính */
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 9998;
        pointer-events: none;
        
        padding: 4px; /* Dày bằng viền chính */
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: spin 4s linear infinite;
        
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;

        /* ĐÂY LÀ PHÉP THUẬT: Làm nhòe cực mạnh để tạo sương */
        filter: blur(20px); 
        opacity: 1; /* Tăng độ sáng lên tối đa */
    }
    /* ẨN GIAO DIỆN CŨ */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- ANIMATION GÓC XOAY --- */
    @property --angle {
      syntax: '<angle>';
      initial-value: 0deg;
      inherits: false;
    }
    @keyframes spin {
        to { --angle: 360deg; }
    }
    .liquid-glass {
        position: relative;
        background: rgba(255, 255, 255, 0.001); 
        
        backdrop-filter: blur(2px); 
        -webkit-backdrop-filter: blur(2px);
        
        border-radius: 35px;
        padding: 12px 25px;
        margin-bottom: 15px;
        color: white;
        font-weight: 500;
        display: flex; align-items: center;
        z-index: 1;
        
        border: 1px solid rgba(255,255,255,0.05);
        
        width: fit-content; max-width: 85%;
    }
    .liquid-glass::before {
        content: "";
        position: absolute;
        inset: 0;
        z-index: -1;
        border-radius: 35px; 
        padding: 2px;
        
        /* Quan trọng: Màu đầu (#00C6FF) và màu cuối (#00C6FF) PHẢI GIỐNG NHAU để xoay không bị giật */
        background: conic-gradient(
            from var(--angle), 
            #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00, #E0C3FC, #00C6FF
        );
        
        animation: spin 6s linear infinite;
        
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        
        /* Glow nhẹ */
        filter: blur(10px);
    }
    
    /* Lớp Glow loe sáng bên ngoài */
    .liquid-glass::after {
        content: "";
        position: absolute;
        inset: -4px;
        z-index: -4;
        border-radius: 35px;
        background: conic-gradient(
            from var(--angle), 
            #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00, #E0C3FC, #00C6FF
        );
        animation: spin 4s linear infinite;
        filter: blur(20px); /* Độ loe sáng */
        opacity: 0.7;
    }

    /* Căn chỉnh hàng chat */
    .icon { margin-right: 12px; font-size: 1.5rem; }
    .user-row { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }

    /* ================= GIAO DIỆN NHƯ ẢNH 2 ================= */
    /* --- Style cho Thanh công cụ Upload (Expander) --- */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.1) !important; /* Nền trong suốt nhẹ */
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        font-weight: 500 !important;
    }
    [data-testid="stExpander"] {
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 10px; /* Khoảng cách với thanh chat */
    }
    /* Nội dung bên trong expander */
    [data-testid="stExpander"] .streamlit-expanderContent {
        background-color: rgba(0,0,0,0.3) !important;
        border-radius: 0 0 15px 15px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-top: none !important;
    }
    
    /* --- Style cho Thanh Chat Input --- */
    .stChatInputContainer {
        padding-bottom: 30px;
    }
    /* Áp dụng style Neon cho khung nhập liệu */
    .stChatInputContainer > div {
        border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important;
        background: rgba(0, 0, 0, 0.7) !important; /* Nền tối hơn chút để dễ đọc chữ */
        color: white !important;
        border: none !important;
        padding-left: 15px !important;
    }

    /* Tối ưu khoảng cách container chính */
    .block-container { padding-bottom: 100px !important; }
</style>
""", unsafe_allow_html=True)
# --- LOGIC CHẶN ĐĂNG NHẬP ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None

if not st.session_state.logged_in:
    st.markdown("""
        <div class="title-container" style="margin-top: 100px;">
            <div class="main-title">🔒 BẢO MẬT</div>
            <div class="sub-title">Hệ thống "Trí tuệ nhân tạo của Le Vu"</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        input_sdt = st.text_input("Số điện thoại:", placeholder="Nhập SĐT của bạn...")
        input_key = st.text_input("Mã Key:", type="password", placeholder="Nhập Key kích hoạt...", label_visibility="visible")
        
        if st.button("ĐĂNG NHẬP 🚀", use_container_width=True):
            success, role, msg = kiem_tra_dang_nhap(input_key, input_sdt)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    st.stop()
# --- PANEL QUẢN LÝ (ADMIN MỚI) ---
if st.session_state.get("user_role") == "admin":
    with st.expander("🛠️ ADMIN: TẠO KEY BÁN HÀNG", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            sdt_input = st.text_input("SĐT Khách hàng", placeholder="09xxxx")
            note_input = st.text_input("Ghi chú", placeholder="Tên khách")
        
        with c2:
            # Menu chọn thời hạn
            option_time = st.selectbox(
                "Gói thời gian:",
                ("Dùng thử (1 ngày)", "1 Tuần (7 ngày)", "1 Tháng (30 ngày)", "3 Tháng (90 ngày)", "1 Năm (365 ngày)", "Vĩnh viễn (10 năm)")
            )
            
            # Logic đổi lựa chọn thành số ngày
            days_map = {
                "Dùng thử (1 ngày)": 1,
                "1 Tuần (7 ngày)": 7,
                "1 Tháng (30 ngày)": 30,
                "3 Tháng (90 ngày)": 90,
                "1 Năm (365 ngày)": 365,
                "Vĩnh viễn (10 năm)": 3650
            }
            so_ngay = days_map[option_time]
            
            st.write("")
            if st.button("Tạo Key & Lưu", use_container_width=True):
                if sdt_input:
                    k, han_dung = tao_key_moi(sdt_input, note_input, so_ngay)
                    st.success(f"✅ Tạo thành công! Hết hạn ngày: {han_dung}")
                    st.code(k, language="text")
                else:
                    st.warning("Thiếu SĐT kìa sếp ơi!")
# Tạo container để chứa lịch sử chat, nằm bên trên khu vực nhập liệu
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">⭐</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="bot-row"><div class="liquid-glass"><span class="icon">🤖</span> <div>{message["content"]}</div></div></div>""", unsafe_allow_html=True)

# --- 7. KHU VỰC NHẬP LIỆU (BỐ CỤC NHƯ ẢNH 2) ---
# Tạo container cố định ở đáy để chứa công cụ và thanh chat
with st.container():
    # 7.1. Thanh công cụ upload (Dạng Expander nằm trên)
    with st.expander("📸 Tải ảnh lên (Nếu cần)", expanded=False):
        uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        image_to_send = None
        if uploaded_file:
            image_to_send = Image.open(uploaded_file)
            st.image(image_to_send, width=50, caption="Ảnh đã chọn")
            st.caption("✅ Ảnh đã sẵn sàng. Nhấn Enter để gửi.")

    # 7.2. Thanh Chat Input (Nằm ngay dưới)
    user_input = st.chat_input("Nhập tin nhắn của bạn...")

# --- 8. XỬ LÝ LOGIC GỬI TIN ---
if user_input: # Chỉ gửi khi người dùng nhập chữ và nhấn Enter
    
    display_text = user_input
    if image_to_send:
        display_text = f"[Đã gửi kèm ảnh] <br> {user_input}"

    # Hiện tin nhắn User ngay lập tức vào lịch sử
    with chat_container:
        st.markdown(f"""<div class="user-row"><div class="liquid-glass"><span class="icon">⭐</span> <div>{display_text}</div></div></div>""", unsafe_allow_html=True)
        if image_to_send:
            with st.chat_message("user", avatar=None): # Dùng container chuẩn để hiện ảnh cho đẹp
                st.image(image_to_send, width=300)
    
    # Lưu vào session state
    st.session_state.messages.append({"role": "user", "content": display_text})

  # --- PHẦN GỬI TIN & XỬ LÝ STREAMING (Đã sửa lỗi config=) ---
    try:
        inputs = [user_input]
        if image_to_send:
            inputs.append(image_to_send)

        with chat_container:
            with st.spinner("Le Vu Intelligence đang suy nghĩ...."):
                # BỎ DÒNG st.markdown(...) ĐỂ HIỆN KHUNG CHAT RỖNG Ở ĐÂY
                
                # Tạo một placeholder duy nhất để cập nhật nội dung
                bot_message_placeholder = st.empty() 
                full_bot_reply = ""
                
                response_stream = st.session_state.chat_session.send_message(
                    content=inputs,
                    stream=True
                )
                
                # Duyệt qua từng đoạn response và CẬP NHẬT placeholder
                for chunk in response_stream:
                    if chunk.text:
                        full_bot_reply += chunk.text
                        bot_message_placeholder.markdown(f"""
                        <div class="bot-row">
                            <div class="liquid-glass">
                                <span class="icon">🤖</span> 
                                <div>{full_bot_reply}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                bot_reply = full_bot_reply # Lưu kết quả cuối cùng

        # Lưu vào session state sau khi stream xong
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        with chat_container:
            st.error(f"Lỗi: {e}")