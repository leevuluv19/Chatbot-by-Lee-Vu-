import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (FULL RAINBOW BORDER + LIQUID GLASS) ---
st.markdown("""
<style>
    /* 1. NỀN LIQUID DARK */
    .stApp {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    /* Lớp phủ tối */
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); z-index: -1;
    }

    /* 2. ẨN GIAO DIỆN CŨ */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- 3. ANIMATION 7 MÀU CHẠY --- */
    @keyframes rainbow-run {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* --- 4. STYLE KHUNG CHAT (ÁP DỤNG CHO CẢ 2) --- */
    .liquid-glass {
        position: relative;
        
        /* Nền kính trong suốt (Đen mờ 10%) */
        background: rgba(0, 0, 0, 0.3); 
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        
        border-radius: 25px;
        padding: 15px 25px;
        margin-bottom: 15px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        z-index: 1;
        max-width: 50%;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* --- KỸ THUẬT TẠO VIỀN 7 MÀU CHẠY (MASK COMPOSITE) --- */
    .liquid-glass::before {
        content: "";
        position: absolute;
        inset: 0; /* Phủ kín khung */
        border-radius: 25px; 
        padding: 2px; /* ĐỘ DÀY VIỀN */
        
        /* Dải màu cầu vồng */
        background: linear-gradient(
            90deg, 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        background-size: 400%; /* Kéo dài dải màu */
        
        /* Animation chạy liên tục */
        animation: rainbow-run 10s linear infinite;
        
        /* --- PHÉP THUẬT ĐỤC LỖ --- */
        /* Dùng mask để đục thủng phần giữa, chỉ giữ lại viền */
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        
        pointer-events: none;
    }

    .icon {
        font-size: 1.8rem;
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));
    }

    /* CĂN CHỈNH VỊ TRÍ */
    /* Sếp (User) -> Căn Phải */
    .user-row { 
        display: flex; 
        justify-content: flex-end; 
    }
    .user-row .liquid-glass {
        flex-direction: row-reverse; /* Icon nằm bên phải */
        border-top-right-radius: 5px; /* Góc nhọn */
    }
    .user-row .icon { margin-left: 15px; margin-right: 0; }

    /* Bot (Anh Trai) -> Căn Trái */
    .bot-row { 
        display: flex; 
        justify-content: flex-start; 
    }
    .bot-row .liquid-glass {
        border-top-left-radius: 5px; /* Góc nhọn */
    }
    .bot-row .icon { margin-right: 15px; }


    /* --- KHUNG NHẬP LIỆU (CŨNG 7 MÀU) --- */
    .stChatInputContainer { padding: 20px 0; }
    .stChatInputContainer > div {
        position: relative; border-radius: 30px; padding: 2px;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        background-size: 400%;
        animation: rainbow-run 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important;
        background: rgba(0, 0, 0, 0.6) !important;
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
        # Sếp chat (Căn phải)
        st.markdown(f"""
            <div class="user-row">
                <div class="liquid-glass">
                    <span class="icon">🔴</span>
                    <div>{message["content"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Bot chat (Căn trái)
        st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass">
                    <span class="icon">🤖</span>
                    <div>{message["content"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # Hiển thị User
    st.markdown(f"""
        <div class="user-row">
            <div class="liquid-glass">
                <span class="icon">🔴</span>
                <div>{user_input}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        # Hiển thị Bot
        st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass">
                    <span class="icon">🤖</span>
                    <div>{bot_reply}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")