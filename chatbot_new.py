import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS "LIQUID GLASS + APPLE INTELLIGENCE" ---
st.markdown("""
<style>
    /* 1. NỀN LIQUID (Dùng đúng ảnh Sếp gửi) */
    .stApp {
        background-image: url("https://img.freepik.com/free-photo/abstract-black-oil-paint-texture-background_53876-102366.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    /* Lớp phủ tối để chữ dễ đọc hơn */
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); z-index: -1;
    }

    /* 2. ẨN GIAO DIỆN MẶC ĐỊNH */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;} /* Ẩn Avatar */
    .stChatMessage {background: transparent !important; border: none !important;}

    /* 3. STYLE KHUNG CHAT (GLASS + APPLE BORDER) */
    .apple-glass {
        position: relative;
        backdrop-filter: blur(20px); /* Kính mờ */
        -webkit-backdrop-filter: blur(20px);
        border-radius: 25px;
        padding: 15px 25px;
        margin-bottom: 20px;
        color: white;
        font-weight: 500;
        display: flex;
        align-items: center;
        width: fit-content;
        max-width: 85%;
        
        /* Kỹ thuật tạo viền cầu vồng gradient */
        border: 2px solid transparent;
        background-clip: padding-box, border-box;
        background-origin: padding-box, border-box;
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                          linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #00ff00, #0000ff, #4b0082, #9400d3);
        
        box-shadow: 0 5px 15px rgba(0,0,0,0.3); /* Bóng đổ */
    }

    /* Hiệu ứng Glow (Phát sáng) xung quanh */
    .apple-glass::before {
        content: ""; position: absolute;
        top: -2px; left: -2px; right: -2px; bottom: -2px;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #00ff00, #0000ff, #4b0082, #9400d3);
        z-index: -1;
        border-radius: 26px;
        filter: blur(10px); /* Làm nhòe để tạo glow */
        opacity: 0.5;
    }

    .icon {
        font-size: 1.8rem; margin-right: 15px;
        filter: drop-shadow(0 0 2px rgba(255,255,255,0.8));
    }

    /* Căn chỉnh Trái - Phải */
    .user-container { display: flex; justify-content: flex-end; }
    .bot-container { display: flex; justify-content: flex-start; }

    /* 4. KHUNG NHẬP LIỆU (VIỀN CẦU VỒNG) */
    .stChatInputContainer { padding: 30px 0; }
    .stChatInputContainer > div {
        border-radius: 35px; padding: 3px;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    .stChatInputContainer textarea {
        border-radius: 32px !important;
        background: rgba(0, 0, 0, 0.7) !important;
        color: white !important; border: none !important;
    }

    /* 5. TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 40px; margin-top: 20px; }
    .main-title {
        font-size: 3rem; font-weight: 800; color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
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
        # Tin nhắn của Sếp (Căn phải + Viền cầu vồng)
        st.markdown(f"""
            <div class="user-container">
                <div class="apple-glass">
                    <span class="icon">🔴</span>
                    {message["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Tin nhắn của Bot (Căn trái + Viền cầu vồng)
        st.markdown(f"""
            <div class="bot-container">
                <div class="apple-glass">
                    <span class="icon">🤖</span>
                    {message["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # Hiển thị User
    st.markdown(f"""
        <div class="user-container">
            <div class="apple-glass">
                <span class="icon">🔴</span>
                {user_input}
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Gửi cho AI
    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        # Hiển thị Bot
        st.markdown(f"""
            <div class="bot-container">
                <div class="apple-glass">
                    <span class="icon">🤖</span>
                    {bot_reply}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")