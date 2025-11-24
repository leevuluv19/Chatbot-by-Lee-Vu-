import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (FULL MÀN HÌNH + VIỀN SƯƠNG MÙ) ---
st.markdown("""
<style>
    /* --- FIX LỖI FULL MÀN HÌNH (QUAN TRỌNG) --- */
    
    /* 1. Áp dụng ảnh nền cho Container chính của Streamlit */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* 2. Làm trong suốt thanh Header trên cùng */
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }

    /* 3. Xóa khoảng trắng thừa thãi ở trên và dưới */
    .block-container {
        padding-top: 20px !important;
        padding-bottom: 40px !important;
    }

    /* Lớp phủ tối mờ toàn màn hình */
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.3); 
        z-index: -1; pointer-events: none;
    }

    /* --- ẨN GIAO DIỆN CŨ --- */
    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- VIỀN SƯƠNG MÙ 7 MÀU (FOGGY RAINBOW) CHO WEB --- */
    @property --angle {
      syntax: '<angle>';
      initial-value: 0deg;
      inherits: false;
    }
    @keyframes spin {
        to { --angle: 360deg; }
    }

    /* LỚP 1: LÕI SƯƠNG (Sát mép) */
    body::before {
        content: ""; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        z-index: 9999; pointer-events: none;
        padding: 8px; /* Độ dày viền */
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        filter: blur(10px); /* Nhòe nhẹ */
        opacity: 0.8;
    }
    
    /* LỚP 2: HƠI SƯƠNG LAN TỎA (Loe rộng) */
    body::after {
        content: ""; position: fixed;
        top: -20px; left: -20px; right: -20px; bottom: -20px;
        z-index: 9998; pointer-events: none;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        filter: blur(40px); /* Nhòe cực mạnh tạo sương */
        opacity: 0.5;
    }

    /* --- STYLE KHUNG CHAT (LIQUID GLASS) --- */
    .liquid-glass {
        position: relative;
        background: rgba(0, 0, 0, 0.2); /* Trong suốt */
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border-radius: 25px; padding: 15px 20px; margin-bottom: 15px;
        color: #ffffff; font-weight: 500;
        display: flex; align-items: center; z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Viền chat 7 màu chạy */
    .liquid-glass::before {
        content: ""; position: absolute; inset: 0; border-radius: 25px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        pointer-events: none; z-index: -1; filter: blur(2px);
    }

    .icon { margin-right: 15px; font-size: 1.5rem; filter: drop-shadow(0 0 5px rgba(255,255,255,0.8)); }
    .user-row { display: flex; justify-content: flex-end; }
    .bot-row { display: flex; justify-content: flex-start; }

    /* --- KHUNG INPUT --- */
    .stChatInputContainer { padding-bottom: 30px; }
    .stChatInputContainer > div {
        position: relative; border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important; backdrop-filter: blur(10px);
    }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 30px; margin-top: -20px; }
    .main-title { font-size: 2.5rem; font-weight: bold; color: white; text-shadow: 0 0 10px rgba(255,255,255,0.5); }
    .sub-title { font-size: 1rem; color: rgba(255,255,255,0.7); }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">Le Vu Intelligence</div>
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

# --- 6. HIỂN THỊ LỊCH SỬ CHAT ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="user-row">
                <div class="liquid-glass">
                    <span class="icon">🔴</span>
                    <div>{message["content"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
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