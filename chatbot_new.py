import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (ĐỒNG BỘ GIAO DIỆN CAPSULE) ---
st.markdown("""
<style>
    /* 1. NỀN LIQUID DARK FULL MÀN HÌNH */
    html, body, .stApp {
        height: 100vh; width: 100vw; margin: 0; padding: 0;
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        overflow-x: hidden;
    }
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.3); z-index: -1; pointer-events: none;
    }

    /* 2. ẨN GIAO DIỆN CŨ */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* 3. ANIMATION XOAY TRÒN */
    @property --angle {
      syntax: '<angle>';
      initial-value: 0deg;
      inherits: false;
    }
    @keyframes rainbow-spin {
        to { --angle: 360deg; }
    }

    /* --- 4. STYLE KHUNG CHAT (HÌNH VIÊN THUỐC - CAPSULE) --- */
    .liquid-glass {
        position: relative;
        
        /* Nền kính trong suốt */
        background: rgba(0, 0, 0, 0.2); 
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        
        /* BO TRÒN MẠNH (35px) ĐỂ GIỐNG VIÊN THUỐC */
        border-radius: 35px; 
        
        padding: 12px 25px; /* Khung gọn gàng hơn */
        margin-bottom: 15px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        z-index: 1;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        
        /* Giới hạn chiều rộng để đẹp hơn */
        width: fit-content;
        max-width: 80%;
    }

    /* VIỀN 7 MÀU CHẠY NỐI ĐUÔI */
    .liquid-glass::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 35px; /* Bo khớp với khung */
        padding: 2px; /* Viền mỏng tinh tế */
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: rainbow-spin 4s linear infinite;
        
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        
        pointer-events: none;
        z-index: -1;
        filter: blur(2px);
    }

    .icon {
        margin-right: 15px; font-size: 1.5rem;
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.8));
    }

    /* CĂN CHỈNH */
    .user-row { display: flex; justify-content: flex-end; }
    .bot-row { display: flex; justify-content: flex-start; }

    /* KHUNG INPUT (ĐỒNG BỘ STYLE) */
    .stChatInputContainer { padding: 20px 0; }
    .stChatInputContainer > div {
        position: relative; border-radius: 35px; padding: 2px;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        background-size: 400%;
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 33px !important;
        background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important;
        backdrop-filter: blur(10px);
    }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 30px; padding-top: 20px; }
    .main-title {
        font-size: 2.5rem; font-weight: bold; color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
    }
    .sub-title { font-size: 1rem; color: rgba(255,255,255,0.7); }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ ---
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
    st.error("⚠️ Chưa có chìa khóa! Vào Settings -> Secrets để điền API Key.")
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

# --- 6. HIỂN THỊ LỊCH SỬ CHAT ---
for message in st.session_state.messages:
    if message["role"] == "user":
        # Sếp chat
        st.markdown(f"""
            <div class="user-row">
                <div class="liquid-glass">
                    <span class="icon">🔴</span>
                    <div>{message["content"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Bot chat
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