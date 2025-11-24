import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ AI", page_icon="", layout="centered")

# --- 2. CSS SIÊU CẤP (APPLE INTELLIGENCE GLOW + VISION OS GLASS) ---
st.markdown("""
<style>
    /* --- NỀN FULL MÀN HÌNH --- */
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
        background: rgba(0, 0, 0, 0.2); /* Giảm độ tối để nền liquid nổi hơn */
        z-index: -1; pointer-events: none;
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

    /* --- KHUNG CHAT CHUẨN APPLE (VISION OS GLASS) --- */
    .liquid-glass {
        position: relative;
        
        /* Nền kính siêu trong (Apple Style) */
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(25px) saturate(180%); /* Blur mạnh + Tăng bão hòa màu nền */
        -webkit-backdrop-filter: blur(25px) saturate(180%);
        
        /* Bo tròn mạnh hình viên thuốc (Capsule) */
        border-radius: 35px;
        padding: 12px 25px;
        margin-bottom: 15px;
        color: white;
        font-weight: 500;
        display: flex; align-items: center;
        z-index: 1;
        
        /* Hiệu ứng bóng kính phản chiếu nhẹ bên trên */
        box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.2), 0 4px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1); /* Viền kính mỏng */
        
        width: fit-content; max-width: 85%;
    }

    /* --- VIỀN PHÁT SÁNG APPLE INTELLIGENCE --- */
    .liquid-glass::before {
        content: "";
        position: absolute;
        inset: -2px; /* Viền dày 2px */
        z-index: -1;
        border-radius: 36px; 
        
        /* Dải màu Apple Intelligence Chính Hãng (Cyan - Blue - Purple - Pink - Orange) */
        background: conic-gradient(
            from var(--angle), 
            transparent 30%,
            #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00, #00C6FF
        );
        
        animation: spin 4s linear infinite;
        filter: blur(8px); /* Loe sáng mạnh (Glow) */
        opacity: 0.8;
    }
    
    /* Lớp viền sắc nét bên trong (để định hình rõ hơn) */
    .liquid-glass::after {
        content: "";
        position: absolute;
        inset: 0;
        z-index: -1;
        border-radius: 35px;
        background: rgba(0,0,0,0.4); /* Lớp nền tối nhẹ sau kính để chữ rõ hơn */
    }

    .icon {
        margin-right: 15px; font-size: 1.6rem;
        filter: drop-shadow(0 0 8px rgba(255,255,255,0.6));
    }

    /* CĂN CHỈNH */
    .user-row { display: flex; justify-content: flex-end; }
    .bot-row { display: flex; justify-content: flex-start; }

    /* --- KHUNG NHẬP LIỆU ĐỒNG BỘ --- */
    .stChatInputContainer { padding: 20px 0; }
    .stChatInputContainer > div {
        position: relative; border-radius: 35px; padding: 2px;
        background: conic-gradient(from var(--angle), #00C6FF, #8E2DE2, #F80759, #FF8C00, #00C6FF);
        animation: spin 4s linear infinite;
        box-shadow: 0 0 20px rgba(0, 198, 255, 0.3);
    }
    .stChatInputContainer textarea {
        border-radius: 33px !important;
        background: rgba(0, 0, 0, 0.5) !important;
        color: white !important; border: none !important;
        backdrop-filter: blur(20px);
    }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 30px; padding-top: 20px; }
    .main-title {
        font-size: 2.5rem; font-weight: 800; color: white;
        background: -webkit-linear-gradient(0deg, #00C6FF, #0072FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 198, 255, 0.3);
    }
    .sub-title { font-size: 1rem; color: rgba(255,255,255,0.8); font-weight: 300; }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">Lê Vũ Intelligence</div>
        <div class="sub-title">Designed by Le Van Vu</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. CẤU HÌNH API ---
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

# --- 6. HIỂN THỊ LỊCH SỬ ---
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
user_input = st.chat_input("Nhập tin nhắn...")

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