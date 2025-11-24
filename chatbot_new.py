import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (NỀN LIQUID + KHUNG KÍNH + VIỀN APPLE) ---
st.markdown("""
<style>
    /* --- NỀN LIQUID DARK --- */
    .stApp {
        /* Link ảnh nền chất lỏng tối */
        background-image: url("https://img.freepik.com/free-photo/abstract-black-oil-paint-texture-background_53876-102366.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    /* Lớp phủ tối để làm nổi bật nội dung */
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); z-index: -1;
    }

    /* --- ẨN CÁC THÀNH PHẦN MẶC ĐỊNH --- */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;} /* Ẩn avatar gốc */

    /* --- STYLE CHUNG CHO KHUNG KÍNH (LIQUID GLASS) --- */
    .liquid-glass {
        backdrop-filter: blur(20px); /* Kính mờ */
        -webkit-backdrop-filter: blur(20px);
        background: rgba(255, 255, 255, 0.05); /* Trong suốt */
        border-radius: 25px;
        padding: 15px 25px;
        margin-bottom: 20px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        box-shadow: inset 0 0 15px rgba(255,255,255,0.05);
        
        /* VIỀN APPLE 7 MÀU */
        border: 2px solid transparent; 
        background-clip: padding-box, border-box;
        background-origin: padding-box, border-box;
        background-image: linear-gradient(rgba(255,255,255,0.05), rgba(255,255,255,0.05)), 
                          linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #00ff00, #0000ff, #4b0082, #9400d3);
        position: relative;
    }

    /* Hiệu ứng Glow phát sáng xung quanh */
    .liquid-glass::before {
        content: ""; position: absolute;
        top: -3px; left: -3px; right: -3px; bottom: -3px;
        z-index: -1; border-radius: 28px;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #00ff00, #0000ff, #4b0082, #9400d3);
        filter: blur(10px); opacity: 0.4;
    }

    .liquid-glass .icon {
        margin-right: 15px; font-size: 1.8rem;
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));
    }

    /* --- KHUNG NHẬP LIỆU (VIỀN CẦU VỒNG) --- */
    .stChatInputContainer { padding: 30px 0; }
    .stChatInputContainer > div {
        position: relative; border-radius: 35px; padding: 3px;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    .stChatInputContainer textarea {
        border-radius: 32px !important;
        background: rgba(0, 0, 0, 0.7) !important;
        color: white !important; border: none !important;
    }

    /* --- TIÊU ĐỀ --- */
    .title-container { text-align: center; margin-bottom: 40px; margin-top: 20px; }
    .main-title {
        font-size: 3rem; font-weight: 800; color: white;
        text-shadow: 0 0 15px rgba(255,255,255,0.4);
    }
    .sub-title { font-size: 1.1rem; color: rgba(255,255,255,0.7); margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">😎 Lê Vũ Depzai (Anh Trai)</div>
        <div class="sub-title">Trò chuyện cùng anh Lê Vũ</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. CẤU HÌNH API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
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

# --- 6. HIỂN THỊ LỊCH SỬ CHAT ---
for message in st.session_state.messages:
    if message["role"] == "user":
        # Tin nhắn của Sếp (Icon Đỏ)
        st.markdown(f"""
            <div class="liquid-glass">
                <span class="icon">🔴</span>
                {message["content"]}
            </div>
        """, unsafe_allow_html=True)
    else:
        # Tin nhắn của Bot (Icon Robot Vàng)
        st.markdown(f"""
            <div class="liquid-glass">
                <span class="icon">🤖</span>
                {message["content"]}
            </div>
        """, unsafe_allow_html=True)

# --- 7. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # Hiển thị User
    st.markdown(f"""
        <div class="liquid-glass">
            <span class="icon">🔴</span>
            {user_input}
        </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Gửi cho AI
    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        # Hiển thị Bot
        st.markdown(f"""
            <div class="liquid-glass">
                <span class="icon">🤖</span>
                {bot_reply}
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        # Bắt lỗi (ĐÂY LÀ CHỖ SẾP HAY COPY THIẾU)
        st.markdown(f"""
            <div class="liquid-glass" style="border-color: red;">
                <span class="icon">⚠️</span> Lỗi kết nối: {e}
            </div>
        """, unsafe_allow_html=True)