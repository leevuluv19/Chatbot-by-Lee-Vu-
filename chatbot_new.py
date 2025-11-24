import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS TÙY CHỈNH GIAO DIỆN (Bản sao y hệt ảnh) ---
BACKGROUND_IMAGE_PATH = "/mnt/data/dfed2b2c-3820-4934-a52d-caa7a063c8d2.png"

st.markdown(f"""
<style>

html, body {{
    background: url("{BACKGROUND_IMAGE_PATH}") no-repeat center center fixed;
    background-size: cover;
}}

#MainMenu, footer, header {{visibility: hidden;}}

.liquid-glass {{
    position: relative; 
    z-index: 1;
    backdrop-filter: blur(20px) saturate(120%);
    -webkit-backdrop-filter: blur(20px) saturate(120%);
    background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    border-radius: 28px;
    padding: 18px 22px;
    margin-bottom: 18px;
    color: #ffffff;
    font-weight: 500;
    display: flex;
    align-items: center;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    overflow: hidden;
}}

.liquid-glass::after {{
    content: "";
    position: absolute;
    top: -40%; left: -30%;
    width: 60%; height: 160%;
    background: linear-gradient(120deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02) 40%, rgba(255,255,255,0) 60%);
    transform: rotate(-20deg);
    filter: blur(12px);
    opacity: 0.8;
    pointer-events: none;
}}

.icon {{
    margin-right: 15px;
    font-size: 1.8rem;
    filter: drop-shadow(0 0 8px rgba(255,255,255,0.6));
}}

.user-bubble {{
    border-color: rgba(255, 50, 50, 0.75) !important;
    box-shadow: 0 0 24px rgba(255, 40, 40, 0.35), inset 0 0 12px rgba(255, 40, 40, 0.12) !important;
    background: linear-gradient(135deg, rgba(255,50,50,0.06), rgba(0,0,0,0)) !important;
}}

.bot-bubble {{
    border-color: rgba(255, 180, 0, 0.75) !important;
    box-shadow: 0 0 22px rgba(255, 160, 0, 0.30), inset 0 0 10px rgba(255, 160, 0, 0.10) !important;
    background: linear-gradient(135deg, rgba(255,180,0,0.06), rgba(0,0,0,0)) !important;
}}

.stChatInputContainer {{
    padding: 20px 0; position: relative; z-index: 2;
}}

.stChatInputContainer > div {{
    position: relative;
    border-radius: 40px;
    padding: 3px;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    box-shadow: 0 0 30px rgba(255, 255, 255, 0.12);
}}

.stChatInputContainer textarea {{
    border-radius: 40px !important;
    background: rgba(0, 0, 0, 0.6) !important;
    color: white !important;
    border: none !important;
    padding: 15px 20px !important;
    backdrop-filter: blur(10px);
    width: 100% !important;
    resize: none !important;
}}

.stChatInputContainer button {{
    color: rgba(255,255,255,0.95) !important;
    background: transparent !important;
    border: none !important;
}}

.title-container {{
    text-align: center; 
    margin: 30px 0 20px 0; 
    position: relative; 
    z-index:2;
}}

.main-title {{
    font-size: 2.4rem; 
    font-weight: 800; 
    color: white;
    text-shadow: 0 0 14px rgba(255,255,255,0.12);
    letter-spacing: 0.5px;
}}

.sub-title {{
    font-size: 1rem; 
    color: rgba(255,255,255,0.75);
}}

@media (max-width: 600px) {{
    .main-title {{ font-size: 1.6rem; }}
    .liquid-glass {{ padding: 12px; border-radius: 18px; }}
}}

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
    st.error("⚠️ Chưa có API Key! Vào Settings → Secrets để thêm.")
    st.stop()

# --- 5. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, trưởng thành."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. HIỂN THỊ LỊCH SỬ CHAT ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="liquid-glass user-bubble">
                <span class="icon">🔴</span>
                <div style="flex:1">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <span class="icon">🤖</span>
                <div style="flex:1">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. NHẬN TIN NHẮN ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    st.markdown(f"""
        <div class="liquid-glass user-bubble">
            <span class="icon">🔴</span>
            <div style="flex:1">{user_input}</div>
        </div>
    """, unsafe_allow_html=True)

    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text if hasattr(response, 'text') else str(response)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <span class="icon">🤖</span>
                <div style="flex:1">{bot_reply}</div>
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
            <div class="liquid-glass user-bubble" style="border-color:#ff0000;">
                <span class="icon">⚠️</span>
                <div style="flex:1">Lỗi kết nối: {e}</div>
            </div>
        """, unsafe_allow_html=True)
