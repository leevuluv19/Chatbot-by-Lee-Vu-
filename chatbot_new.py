import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS HIỆU ỨNG "SAO CHỔI NEON" (CHASING TAIL + GLOW) ---
st.markdown("""
<style>
    /* 1. NỀN LIQUID (Ảnh Sếp chọn) */
    .stApp {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); z-index: -1;
    }

    /* 2. ẨN GIAO DIỆN CŨ */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- 4. STYLE KHUNG CHAT "CHASING NEON" --- */
    .neon-box {
        position: relative;
        border-radius: 20px; 
        overflow: hidden; /* Cắt bỏ phần thừa của hiệu ứng quay */
        padding: 2px; /* ĐỘ DÀY VIỀN (2px) */
        margin-bottom: 15px;
        width: fit-content;
        max-width: 85%;
        display: flex; 
        z-index: 1;
    }

    /* LỚP 1: CON RẮN 7 MÀU QUAY TRÒN (::before) */
    .neon-box::before {
        content: '';
        position: absolute;
        z-index: -2;
        left: -50%; top: -50%; width: 200%; height: 200%;
        
        /* Tạo dải màu nối đuôi: Trong suốt -> Màu đậm */
        background: conic-gradient(
            transparent, 
            transparent, 
            transparent, 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, 
            #ff0000
        );
        
        /* Quay liên tục */
        animation: spin 4s linear infinite; 
    }

    /* LỚP 2: NỀN ĐEN TRONG SUỐT BÊN TRONG (::after) */
    /* Đây là lớp che đi phần giữa để tạo ra cái viền */
    .neon-box::after {
        content: '';
        position: absolute;
        z-index: -1;
        left: 2px; top: 2px; right: 2px; bottom: 2px; /* Thụt vào bằng độ dày viền */
        background: rgba(0, 0, 0, 0.5); /* Đen trong suốt 50% */
        border-radius: 18px;
        backdrop-filter: blur(10px); /* Kính mờ */
    }

    /* Nội dung chữ bên trong */
    .box-content {
        position: relative;
        z-index: 2;
        color: white;
        padding: 12px 20px;
        font-weight: 500;
        display: flex; align-items: center;
    }

    .icon {
        margin-right: 15px; font-size: 1.5rem;
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.8)); /* Icon phát sáng */
    }

    /* CĂN CHỈNH TRÁI - PHẢI */
    .user-row { display: flex; justify-content: flex-end; }
    .bot-row { display: flex; justify-content: flex-start; }

    /* --- KHUNG INPUT CŨNG HIỆU ỨNG Y HỆT --- */
    .stChatInputContainer { padding: 20px 0; }
    .stChatInputContainer > div {
        position: relative; border-radius: 30px; overflow: hidden; padding: 2px;
        background-color: transparent;
        box-shadow: 0 0 15px rgba(255,255,255,0.1); /* Glow nhẹ */
    }
    /* Tạo hiệu ứng chạy cho Input */
    .stChatInputContainer > div::before {
        content: ''; position: absolute; z-index: -1;
        left: -50%; top: -50%; width: 200%; height: 200%;
        background: conic-gradient(transparent, transparent, #ff0000, #ffff00, #00ff00, #0000ff, #9400d3, #ff0000);
        animation: spin 3s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important;
        background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important;
    }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 30px; }
    .main-title {
        font-size: 2.5rem; font-weight: bold; color: white;
        text-shadow: 0 0 15px #00ffff; /* Tiêu đề phát sáng xanh */
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
        # Sếp chat
        st.markdown(f"""
            <div class="user-row">
                <div class="neon-box">
                    <div class="box-content">
                        <span class="icon">🔴</span> {message["content"]}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Bot chat
        st.markdown(f"""
            <div class="bot-row">
                <div class="neon-box">
                    <div class="box-content">
                        <span class="icon">🤖</span> {message["content"]}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    st.markdown(f"""
        <div class="user-row">
            <div class="neon-box">
                <div class="box-content">
                    <span class="icon">🔴</span> {user_input}
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        st.markdown(f"""
            <div class="bot-row">
                <div class="neon-box">
                    <div class="box-content">
                        <span class="icon">🤖</span> {bot_reply}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")