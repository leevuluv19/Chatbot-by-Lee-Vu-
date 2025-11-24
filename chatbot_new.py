import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS TÙY CHỈNH GIAO DIỆN (Nền mới + Viền Apple 7 màu) ---
st.markdown("""
<style>
    /* --- NỀN LIQUID DARK MỚI --- */
    .stApp {
        /* Link ảnh nền chất lỏng tối mới, sang trọng hơn */
        background-image: url("https://img.freepik.com/free-photo/black-liquid-marble-background_53876-102367.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    /* Lớp phủ tối để làm nổi bật nội dung */
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.5); z-index: -1; /* Tăng độ tối lên một chút */
    }

    /* --- ẨN CÁC THÀNH PHẦN MẶC ĐỊNH KHÔNG CẦN THIẾT --- */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;} /* Ẩn khung avatar gốc */

    /* --- STYLE CHUNG CHO CÁC KHUNG "LIQUID GLASS" + APPLE BORDER --- */
    .liquid-glass {
        backdrop-filter: blur(20px); /* Hiệu ứng kính mờ mạnh hơn */
        -webkit-backdrop-filter: blur(20px);
        background: rgba(255, 255, 255, 0.05); /* Nền kính trong suốt nhẹ */
        border-radius: 25px; /* Bo tròn nhiều hơn */
        padding: 15px 25px;
        margin-bottom: 20px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        box-shadow: inset 0 0 15px rgba(255,255,255,0.05); /* Bóng kính bên trong */
        
        /* --- VIỀN APPLE INTELLIGENCE (7 MÀU) --- */
        border: 3px solid transparent; /* Viền trong suốt làm nền */
        background-clip: padding-box, border-box;
        background-origin: padding-box, border-box;
        /* Lớp nền bên trong (kính) + Lớp nền viền (gradient cầu vồng) */
        background-image: linear-gradient(rgba(255,255,255,0.05), rgba(255,255,255,0.05)), 
                          linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #00ff00, #0000ff, #4b0082, #9400d3);
        
        /* Hiệu ứng phát sáng cầu vồng nhẹ xung quanh */
        position: relative;
    }
    /* Tạo hiệu ứng glow cầu vồng bằng pseudo-element */
    .liquid-glass::before {
        content: "";
        position: absolute;
        top: -3px; left: -3px; right: -3px; bottom: -3px;
        z-index: -1;
        border-radius: 28px;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #00ff00, #0000ff, #4b0082, #9400d3);
        filter: blur(10px); /* Làm mờ để tạo glow */
        opacity: 0.4; /* Độ trong suốt của glow */
    }

    .liquid-glass .icon {
        margin-right: 15px;
        font-size: 1.8rem; /* Icon lớn hơn chút */
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));
    }

    /* --- KHUNG CHAT CỦA SẾP (User) & BOT (Anh Trai) --- */
    /* (Giờ dùng chung style viền cầu vồng, chỉ khác icon) */
    .user-bubble, .bot-bubble {
        /* Không cần style riêng cho viền nữa */
    }

    /* --- KHUNG NHẬP LIỆU - VIỀN CẦU VỒNG (Đồng bộ) --- */
    .stChatInputContainer {
        padding: 30px 0;
    }
    .stChatInputContainer > div {
        position: relative;
        border-radius: 35px;
        padding: 3px; /* Độ dày viền cầu vồng */
        /* Tạo gradient cầu vồng */
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        box-shadow: 0 0 25px rgba(255, 255, 255, 0.2), 0 0 10px rgba(255,255,255,0.1) inset; /* Phát sáng mạnh hơn */
    }
    .stChatInputContainer textarea {
        border-radius: 32px !important;
        background: rgba(0, 0, 0, 0.7) !important; /* Nền tối bên trong */
        color: white !important;
        border: none !important;
        padding: 18px 25px !important;
        backdrop-filter: blur(15px);
        font-size: 1rem;
    }
    /* Style cho nút gửi (Send icon) */
    .stChatInputContainer button {
        color: rgba(255,255,255,0.9) !important;
    }
    .stChatInputContainer button:hover {
        color: #ffffff !important;
        transform: scale(1.1); /* Hiệu ứng phóng to khi di chuột */
        transition: all 0.2s ease;
    }

    /* --- TIÊU ĐỀ & SUBTITLE --- */
    .title-container {
        text-align: center; margin-bottom: 40px; margin-top: 20px;
    }
    .main-title {
        font-size: 3rem; font-weight: 800; color: white;
        text-shadow: 0 0 15px rgba(255,255,255,0.4), 0 0 5px rgba(255,255,255,0.8); /* Chữ phát sáng mạnh hơn */
        letter-spacing: 1px;
    }
    .sub-title {
        font-size: 1.1rem; color: rgba(255,255,255,0.7); margin-top: 10px;
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">😎 Lê Vũ Depzai (Anh Trai)</div>
        <div class="sub-title">Trò chuyện cùng anh Lê Vũ</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. CẤU HÌNH API (BẢO MẬT) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"] # Đảm bảo tên này khớp với trong Secrets của Sếp
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có chìa khóa! Hãy vào Settings -> Secrets để điền API Key.")
    st.stop()

# --- 5. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, ngắn gọn, trưởng thành."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. HIỂN THỊ LỊCH SỬ CHAT (Dùng HTML tùy chỉnh để giống ảnh) ---
for message in st.session_state.messages:
    if message["role"] == "user":
        # Tin nhắn của Sếp: Icon mặt đỏ + Viền cầu vồng
        st.markdown(f"""
            <div class="liquid-glass user-bubble">
                <span class="icon">🔴</span> {message["content"]}
            </div>
        """, unsafe_allow_html=True)
    else:
        # Tin nhắn của Bot: Icon robot vàng + Viền cầu vồng
        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <span class="icon">🤖</span> {message["content"]}
            </div>
        """, unsafe_allow_html=True)

# --- 7. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # 7.1. Hiển thị tin nhắn User ngay lập tức
    st.markdown(f"""
        <div class="liquid-glass user-bubble">