import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (LIQUID GLASS THỰC SỰ + VIỀN APPLE CHẠY) ---
st.markdown("""
<style>
    /* 1. NỀN LIQUID (Ảnh chất lỏng) */
    .stApp {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    /* Lớp phủ tối mờ để chữ dễ đọc */
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.3); z-index: -1;
    }

    /* 2. ẨN GIAO DIỆN CŨ */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- 3. ANIMATION VIỀN CHẠY --- */
    @keyframes rainbow-border {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* --- 4. STYLE KHUNG CHAT (GLASS TRONG SUỐT + VIỀN CHẠY) --- */
    .liquid-glass {
        position: relative;
        
        /* QUAN TRỌNG: Nền đen trong suốt (Alpha = 0.5) */
        background-color: rgba(0, 0, 0, 0.5); 
        
        /* Hiệu ứng kính mờ background */
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        
        border-radius: 20px;
        padding: 15px 20px;
        margin-bottom: 15px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        z-index: 1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* TẠO VIỀN 7 MÀU CHẠY (Lớp lót bên dưới) */
    .liquid-glass::before {
        content: "";
        position: absolute;
        /* Inset -2px nghĩa là viền dư ra 2px */
        top: -2px; left: -2px; right: -2px; bottom: -2px;
        z-index: -1; /* Nằm dưới khung chat */
        border-radius: 22px; 
        
        /* Dải màu Apple Intelligence */
        background: linear-gradient(
            45deg, 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        background-size: 400%;
        
        /* Kích hoạt chạy */
        animation: rainbow-border 5s linear infinite;
        
        /* Làm nhòe viền để tạo hiệu ứng Glow (Phát sáng) */
        filter: blur(2px);
        opacity: 0.8;
    }

    .icon {
        margin-right: 15px; font-size: 1.5rem;
        filter: drop-shadow(0 0 2px rgba(255,255,255,0.8));
    }

    /* CĂN CHỈNH TRÁI - PHẢI */
    .user-row { display: flex; justify-content: flex-end; }
    .bot-row { display: flex; justify-content: flex-start; }

    /* KHUNG INPUT CŨNG TRONG SUỐT + VIỀN CHẠY */
    .stChatInputContainer { padding: 20px 0; }
    .stChatInputContainer > div {
        position: relative; border-radius: 30px; padding: 2px;
        background: linear-gradient(45deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        background-size: 400%;
        animation: rainbow-border 3s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important;
        /* Nền input đen trong suốt */
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important;
        backdrop-filter: blur(10px);
    }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 30px; }
    .main-title {
        font-size: 2.5rem; font-weight: bold; color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
    }
    .sub-title { font-size: 1rem; color: rgba(255,255,255,0.7); }
</style>
""", unsafe_allow_html=True)

# --- 3. TIÊU ĐỀ ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">😎 Lê Vũ Depzai</div>
        <div class="sub-title">Trò chuyện cùng anh Lê Vũ</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. API KEY ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có chìa khóa! Vào Settings -> Secrets để điền.")
    st.stop()

# --- 5. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, ngắn gọn."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. HIỂN THỊ LỊCH SỬ ---
for message in st.session_state.messages:
    if message["role"] == "user":
        # Sếp chat -> Căn phải
        st.markdown(f"""
            <div class="user-row">
                <div class="liquid-glass">
                    <span class="icon">🔴</span> {message["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Bot chat -> Căn trái
        st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass">
                    <span class="icon">🤖</span> {message["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # User
    st.markdown(f"""
        <div class="user-row">
            <div class="liquid-glass">
                <span class="icon">🔴</span> {user_input}
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Bot
    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass">
                    <span class="icon">🤖</span> {bot_reply}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")