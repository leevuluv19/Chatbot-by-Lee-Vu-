import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import secrets
import os
import re
from datetime import datetime, timedelta
from datetime import datetime, timedelta
# --- KHỞI TẠO CÁC BIẾN QUAN TRỌNG (Dán ngay đầu file, sau Import) ---
TRIAL_LIMIT = 3 # Khách chỉ được chat thử 3 câu
# Khởi tạo biến theo dõi lượt dùng thử
if "trial_count" not in st.session_state:
    st.session_state.trial_count = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "extra_knowledge" not in st.session_state:
    # Biến này lưu trữ các bài học được dạy bằng lệnh /day và kiến thức cố định
    st.session_state.extra_knowledge = [
        # --- DANH TÍNH CỦA BOT & ADMIN ---
        "Tôi là trí tuệ nhân tạo được phát triển bởi Admin Lê Vũ.",
        "Phong cách giao tiếp của tôi là ngầu, súc tích và đôi khi hơi tinh nghịch.",
        "Tên đầy đủ của người tạo ra tôi là Lê Văn Vũ, và anh ấy là Admin đẹp trai nhất Thanh Hóa.",
        "Khi khách hàng muốn mua Key hoặc gia hạn, họ cần liên hệ trực tiếp với Admin Lê Vũ qua Zalo.",
        "SDT của ADMIN depzai : 0376274345 "
    ]   
if "chat_session" not in st.session_state:
    try: 
        # 1. TÍNH TOÁN VÀ LƯU NGÀY CHÍNH XÁC (Ví dụ: Thứ Ba, ngày 25/11/2025)
        current_date = datetime.now().strftime("Thứ ba, ngày 25/11/2025") 
    
        lenh_cai_dat = f"""
        Bạn là Lê Vũ Intelligence. Bạn là trợ lý AI cao cấp...
        
        --- DỮ LIỆU THỜI GIAN HIỆN TẠI ---
        NGÀY VÀ GIỜ HỢP LỆ HIỆN TẠI LÀ: {current_date}. 
        Bất cứ khi nào người dùng hỏi về ngày, BẠN PHẢI DÙNG CHÍNH XÁC thông tin này.
        --- KẾT THÚC DỮ LIỆU THỜI GIAN ---
        
        QUY TẮC BẮT BUỘC:
        1. Nếu người dùng hỏi NGÀY/GIỜ hiện tại, BẠN PHẢI DÙNG CHÍNH XÁC thông tin đã được tiêm vào ở trên.
        2. BẠN PHẢI LUÔN SỬ DỤNG TRUY CẬP INTERNET (Google Search) cho các câu hỏi về thời tiết, tin tức, hoặc dữ liệu hiện tại.
        3. ... (Giữ nguyên các quy tắc khác) ...
        """
        
        # 3. KHỞI TẠO MODEL VỚI LỆNH MỚI
        config_search = {
            "tools": [{'googleSearch': {}}] # Lại bỏ tham số config=
        }

        model = genai.GenerativeModel(
            'models/gemini-2.5-flash',
            system_instruction=lenh_cai_dat,
            # KHÔNG CÓ tham số config= ở đây
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

# --- BẮT ĐẦU KHỐI ĐỊNH NGHĨA HÀM CUỐI CÙNG ---

import re # Cần thư viện này cho kiểm tra SDT

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

def kiem_tra_sdt_vietnam(sdt):
    """Kiểm tra SDT Việt Nam 10 số (bắt đầu bằng 0)"""
    if re.fullmatch(r'0\d{9}', sdt):
        return True
    return False

def tao_key_moi(sdt_khach, ghi_chu, so_ngay_dung):
    data = load_data()
    phan_duoi = secrets.token_hex(4).upper() 
    new_key = f"KEY-{phan_duoi[:4]}-{phan_duoi[4:]}"
    
    # Tính ngày hết hạn
    ngay_hien_tai = datetime.now()
    ngay_het_han = ngay_hien_tai + timedelta(days=so_ngay_dung)
    
    data[new_key] = {
        "status": "active", "sdt": sdt_khach, "created_at": ngay_hien_tai.strftime("%Y-%m-%d %H:%M"),
        "expiry_date": ngay_het_han.strftime("%Y-%m-%d %H:%M"), "note": ghi_chu
    }
    save_data(data)
    return new_key, ngay_het_han.strftime("%d/%m/%Y")

def khoa_sdt_trial(sdt_input):
    """Kiểm tra và khóa SDT nếu đã dùng thử."""
    data = load_data()
    
    # 1. Kiểm tra xem SDT đã được đăng ký (mua key) chưa
    for key, info in data.items():
        if info.get("sdt") == sdt_input:
            return True, "🔑 Số điện thoại này đã mua Key, vui lòng đăng nhập!"

    # 2. Kiểm tra xem SDT này đã dùng Trial và bị khóa chưa
    if "TRIAL_LOCK" not in data:
        data["TRIAL_LOCK"] = {}
        
    if sdt_input in data["TRIAL_LOCK"]:
        return True, "❌ Số điện thoại này đã dùng hết lượt dùng thử! Vui lòng mua Key."
    
    # 3. Nếu chưa bị khóa, ta khóa lại và cho dùng thử
    data["TRIAL_LOCK"][sdt_input] = True
    save_data(data)
    return False, None

def kiem_tra_dang_nhap(input_key, input_sdt):
    """Kiểm tra đăng nhập cho User Key hoặc Admin Pass"""
    # 1. Kiểm tra Admin
    if input_key == ADMIN_PASSWORD and input_sdt == SDT_ADMIN:
        return True, "admin", "Chào Sếp Vũ!"
    
    # 2. Kiểm tra User Key
    data = load_data()
    if input_key in data:
        thong_tin = data[input_key]
        
        # Check SĐT và Hạn sử dụng
        if thong_tin.get("sdt") != input_sdt:
            return False, None, f"❌ Sai SĐT đăng ký! Cần hỗ trợ gọi: {SDT_ADMIN}"
        
        han_su_dung_str = thong_tin.get("expiry_date")
        if han_su_dung_str:
            han_su_dung = datetime.strptime(han_su_dung_str, "%Y-%m-%d %H:%M")
            if datetime.now() > han_su_dung:
                return False, None, f"⚠️ Key đã HẾT HẠN! Liên hệ {SDT_ADMIN} để gia hạn."

        con_lai = ""
        if han_su_dung_str:
             so_ngay_con = (han_su_dung - datetime.now()).days
             con_lai = f"(Còn {so_ngay_con} ngày)"

        return True, "user", f"Xin chào {input_sdt}! {con_lai}"
            
    return False, None, f"❌ Key không tồn tại! Vui lòng mua Key bên dưới! "

# --- KẾT THÚC KHỐI ĐỊNH NGHĨA HÀM ---
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
        
        padding: 2px; /* ĐỘ DÀY VIỀN CHỈ 4PX THÔI */
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: spin 1s linear infinite;
        
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
        
        padding: 2px; /* Dày bằng viền chính */
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: spin 1s linear infinite;
        
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;

        /* ĐÂY LÀ PHÉP THUẬT: Làm nhòe cực mạnh để tạo sương */
        filter: blur(20px); 
        opacity: 1; /* Tăng độ sáng lên tối đa */
    }
/* 1. Header Logo (Top Right) */
.header-logo-fixed {
    position: fixed;
    top: 20px;
    right: 40px; /* Căn chỉnh từ lề phải */
    z-index: 1000; 
    font-size: 1.5rem; /* Kích thước nhỏ hơn Logo chính */
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
        background: rgba(255, 255, 255, 0.00001); 
        
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
        
        animation: spin 8s linear infinite;
        
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
        background-color: rgba(255, 255, 255, 0.001) !important; /* Nền trong suốt nhẹ */
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
        border: 1px solid rgba(255,255,255,0.01) !important;
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
.logo-glow {
    text-align: center;
    font-size: 2.5rem; /* Kích thước logo */
    font-weight: 800;
    color: white;
    /* Royal Blue Shadow (Xanh Hoàng Gia: RGB 65, 105, 225) */
    text-shadow: 0 0 12px rgba(65, 105, 225, 1), /* Sáng mạnh */
                 0 0 20px rgba(65, 105, 225, 1); /* Tỏa sáng rộng */
    margin-top: 10px; 
    margin-bottom: 30px;
}
/* --- OVERRIDE STYLE CHO HỘP THÔNG BÁO (st.info, st.error, etc.) --- */
[data-testid="stAlert"] {
    /* NỀN: Làm tối và trong suốt (50% đục) */
    background-color: rgba(0, 0, 0, 0.5) !important; 
    
    /* VIỀN: Làm viền Neon xanh (Tùy chọn: bạn có thể xóa dòng này nếu không thích) */
    border: 1px solid #00C6FF !important; 
    
    border-radius: 10px !important;
    
    /* CHỮ: Đảm bảo chữ trắng để dễ đọc trên nền tối */
    color: white !important; 
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
    # 1. LOGO LE VU INTELLIGENCE (TOP RIGHT)
st.markdown(f"""
<div class="logo-glow header-logo-fixed">
    Le Vu Intelligence
</div>
""", unsafe_allow_html=True)

# 2. FOOTER DESIGNED BY (BOTTOM RIGHT) <--- ĐẢM BẢO ĐOẠN NÀY ĐÃ CÓ
st.markdown("""
<div class="footer-text-fixed">
    Designed by Le Van Vu
</div>
""", unsafe_allow_html=True)

# --- LOGIC NÚT ĐĂNG NHẬP VÀ DÙNG THỬ BẢO MẬT (Thay thế hoàn toàn khối with col2:) ---
if not st.session_state.logged_in:
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        
        # 1. LOGO, INPUTS (SDT, Key)
        st.markdown("""
        <div class="logo-glow">
            LE VU INTELLIGENCE
        </div>
        """, unsafe_allow_html=True)

        input_sdt = st.text_input("Số điện thoại:", placeholder="Nhập SĐT của bạn...")
        input_key = st.text_input("Mã Key:", type="password", placeholder="Nhập Key kích hoạt...", label_visibility="visible")
        
        # 2. NÚT ĐĂNG NHẬP (Key Đã mua)
        if st.button("ĐĂNG NHẬP 🚀", key="login_btn", use_container_width=True):
            success, role, msg = kiem_tra_dang_nhap(input_key, input_sdt)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
        
        # 3. NÚT DÙNG THỬ (Có kiểm tra SDT và Khóa Trial)
        if st.button(f"DÙNG THỬ ({TRIAL_LIMIT} câu)", key="trial_btn", use_container_width=True):
            if not input_sdt or not kiem_tra_sdt_vietnam(input_sdt):
                st.error("⚠️ Vui lòng nhập SĐT Việt Nam hợp lệ để đăng ký dùng thử.")
                st.stop()
                
            is_locked, lock_msg = khoa_sdt_trial(input_sdt)
            if is_locked:
                st.error(lock_msg) 
                st.stop()
            
            # Cho phép dùng thử
            st.session_state.logged_in = True
            st.session_state.user_role = 'trial'
            st.session_state.trial_count = 0
            st.success(f"Chào mừng! Bạn có {TRIAL_LIMIT} câu hỏi để dùng thử.")
            st.rerun()

        # 4. NÚT MUA KEY / LIÊN HỆ ZALO
        if st.button(f"MUA KEY / LH ZALO", key="buy_btn", use_container_width=True):
            st.info("Vui lòng liên hệ Admin qua Zalo để mua Key chính thức!")
            st.markdown(f"""
            <a href="https://zalo.me/{SDT_ADMIN}" target="_blank">
                <button style="background-color: #0088ff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px;">
                    CHAT ZALO VỚI ADMIN 📞
                </button>
            </a>
            """, unsafe_allow_html=True)
            
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
   # --- BẮT ĐẦU if user_input: (Dán đoạn này ngay đầu khối xử lý tin nhắn) ---
    
    # --- LOGIC CHẶN LƯỢT DÙNG THỬ ---
    if st.session_state.get('user_role') == 'trial':
        
        # 1. KIỂM TRA LIMIT: Nếu count >= 3, thực hiện redirect
        if st.session_state.trial_count >= TRIAL_LIMIT:
            st.error(f"❌ Hết lượt dùng thử! Bạn đã dùng hết {TRIAL_LIMIT} câu hỏi. Đang chuyển về màn hình đăng nhập...")
            
            # RESET & REDIRECT
            st.session_state.logged_in = False 
            st.session_state.user_role = None 
            st.session_state.trial_count = 0
            st.rerun() # <--- LỆNH BẮT BUỘC ĐỂ QUAY LẠI TRANG CHỦ
            
        else:
            # 2. Tăng bộ đếm và thông báo lượt còn lại
            st.session_state.trial_count += 1 # Tăng bộ đếm TRƯỚC KHI xử lý tin nhắn
            st.info(f"💡 Lượt dùng thử còn lại: {TRIAL_LIMIT - st.session_state.trial_count} câu.")  
    if user_input.lower().startswith("/day"):
        kien_thuc_moi = user_input[5:].strip() # Lấy nội dung sau /day
        if kien_thuc_moi:
            st.session_state.extra_knowledge.append(kien_thuc_moi)
            
            # Hiển thị thông báo thành công
            st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass" style="background: rgba(0,255,0,0.1); border: 1px solid #00ff00;">
                    <span class="icon">🧠</span> Đã ghi nhớ kiến thức mới: <b>{kien_thuc_moi}</b>. Ảnh sẽ dùng kiến thức này trong các lần trả lời sau.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Xóa tin nhắn khỏi lịch sử hiển thị
            st.session_state.messages.append({"role": "user", "content": user_input})
            # Dừng xử lý, không gửi lên Gemini
            st.stop()
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
        kien_thuc_goi_them = "\n".join(st.session_state.extra_knowledge)
        
        # Xây dựng prompt cuối cùng: Gộp kiến thức + câu hỏi người dùng
        final_prompt = user_input
        if kien_thuc_goi_them:
            final_prompt = f"### KIẾN THỨC BỔ SUNG (ADMIN DẠY):\n{kien_thuc_goi_them}\n\n### YÊU CẦU NGƯỜI DÙNG: {user_input}"
        
        # Chuẩn bị inputs (Thay user_input bằng final_prompt)
        inputs = [final_prompt] 
        if image_to_send is not None:
            inputs.append(image_to_send)
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