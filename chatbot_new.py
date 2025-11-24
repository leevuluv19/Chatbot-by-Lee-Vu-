import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CHỌN ẢNH NỀN (bạn chọn option A: dùng link) ---
BACKGROUND_IMAGE_URL = "https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg"

# --- 3. CSS CHUNG - Liquid glass + rainbow input + bubbles ---
st.markdown(f"""
<style>
/* Nền toàn trang */
html, body, .stApp {{
    height: 100%;
    background-image: url("{BACKGROUND_IMAGE_URL}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    margin: 0;
    padding: 0;
}}

/* Ẩn header/footer menu mặc định */
#MainMenu, header, footer {{ visibility: hidden; }}

/* Trung tâm nội dung */
.block-container {{
    padding-top: 28px;
    padding-bottom: 40px;
    max-width: 820px;
    margin: 0 auto;
}}

/* TIÊU ĐỀ */
.title-container {{
    text-align: center;
    margin-bottom: 20px;
    z-index: 2;
    position: relative;
}}
.main-title {{
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
    text-shadow: 0 4px 20px rgba(0,0,0,0.6), 0 0 10px rgba(255,255,255,0.06);
}}
.sub-title {{
    color: rgba(255,255,255,0.85);
    font-size: 1rem;
}}

/* LIQUID GLASS BASE */
.liquid-glass {{
    position: relative;
    z-index: 3;
    backdrop-filter: blur(20px) saturate(120%);
    -webkit-backdrop-filter: blur(20px) saturate(120%);
    background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    border-radius: 28px;
    padding: 14px 18px;
    margin-bottom: 14px;
    color: #ffffff;
    font-weight: 500;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    overflow: hidden;}}

/* Sheen (ánh sáng lướt) */
.liquid-glass::after {{
    content: "";
    position: absolute;
    top: -40%;
    left: -30%;
    width: 60%;
    height: 160%;
    background: linear-gradient(120deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02) 40%, rgba(255,255,255,0) 60%);
    transform: rotate(-20deg);
    filter: blur(12px);
    opacity: 0.8;
    pointer-events: none;
}}

/* Icon trong bubble */
.icon {{
    margin-top: 4px;
    font-size: 1.9rem;
    filter: drop-shadow(0 0 10px rgba(255,255,255,0.6));
}}

/* USER (đỏ) */
.user-bubble {{
    border: 2px solid rgba(255,50,50,0.75) !important;
    box-shadow: 0 0 28px rgba(255,40,40,0.32), inset 0 0 12px rgba(255,40,40,0.12) !important;
    background: linear-gradient(135deg, rgba(255,50,50,0.06), rgba(0,0,0,0)) !important;
    align-self: flex-end;
    width: 100%;
}}

/* BOT (vàng-cam) */
.bot-bubble {{
    border: 2px solid rgba(255,180,0,0.75) !important;
    box-shadow: 0 0 26px rgba(255,160,0,0.30), inset 0 0 10px rgba(255,160,0,0.10) !important;
    background: linear-gradient(135deg, rgba(255,180,0,0.06), rgba(0,0,0,0)) !important;
    width: 100%;
}}

/* Nội dung text trong bubble */
.bubble-content {{
    flex: 1;
    word-wrap: break-word;
    white-space: pre-wrap;
    line-height: 1.45;
    font-size: 0.98rem;
}}

/* KHUNG NHẬP LIỆU - RAINBOW FRAME */
.stChatInputContainer {{
    padding: 18px 0;
    position: relative;
    z-index: 4;
    margin-top: 8px;
}}
/* Outer rainbow */
.stChatInputContainer > div {{
    position: relative;
    border-radius: 44px;
    padding: 3px;
    background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
    box-shadow: 0 0 36px rgba(255,255,255,0.10);
}}
/* Inner input */
.stChatInputContainer textarea {{
    border-radius: 40px !important;
    background: rgba(0,0,0,0.6) !important;
    color: #fff !important;
    border: none !important;
    padding: 14px 18px !important;
    backdrop-filter: blur(10px);
    width: 100% !important;
    resize: none !important;
    min-height: 56px;
    font-size: 1rem;
}}

/* Send button style fallback */
.stChatInputContainer button {{
    color: rgba(255,255,255,0.95) !important;
    background: transparent !important;
    border: none !important;
}}

/* Scroll area for chat history */
.chat-history {{
    max-height: 60vh;
    overflow-y: auto;
    padding-right: 6px;
}}

/* Responsive tweaks */
@media (max-width: 640px) {{
    .main-title {{ font-size: 1.6rem; }}
    .liquid-glass {{ padding: 12px; border-radius: 18px; }}
    .stChatInputContainer > div {{ border-radius: 34px; }}
}}

</style>
""", unsafe_allow_html=True)

# --- 4. TIÊU ĐỀ ---
st.markdown("""
<div class="title-container">
    <div class="main-title">😎 Lê Vũ Depzai (Anh Trai)</div>
    <div class="sub-title">Trò chuyện cùng anh Lê Vũ</div>
</div>
""", unsafe_allow_html=True)

# --- 5. CẤU HÌNH API (BẢO MẬT) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có API Key! Vào Settings -> Secrets để thêm GOOGLE_API_KEY.")
    st.stop()

# --- 6. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        "models/gemini-2.0-flash",
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, ngắn gọn, trưởng thành."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 7. HIỂN THỊ LỊCH SỬ CHAT ---
# Chat area container
st.markdown('<div class="chat-history">', unsafe_allow_html=True)

for message in st.session_state.messages:
    if message.get("role") == "user":
        st.markdown(f"""
            <div class="liquid-glass user-bubble">
                <div class="icon">🔴</div>
                <div class="bubble-content">{st.session_state.get('escape_html', False) and st.write(message['content']) or message['content']}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <div class="icon">🤖</div>
                <div class="bubble-content">{message['content']}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- 8. NHẬN TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # lưu message vào session trước khi gửi
    st.session_state.messages.append({"role": "user", "content": user_input})

    # hiển thị ngay user bubble
    st.markdown(f"""
        <div class="liquid-glass user-bubble">
            <div class="icon">🔴</div>
            <div class="bubble-content">{user_input}</div>
        </div>
    """, unsafe_allow_html=True)

    try:
        # gửi tới model
        response = st.session_state.chat_session.send_message(user_input)
        # response.text có thể khác tuỳ SDK version
        bot_reply = getattr(response, "text", None) or str(response)

        # lưu và hiển thị reply
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <div class="icon">🤖</div>
                <div class="bubble-content">{bot_reply}</div>
            </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Lỗi: {e}"})
        st.markdown(f"""
            <div class="liquid-glass user-bubble" style="border-color: rgba(255,0,0,0.9); box-shadow: 0 0 28px rgba(255,0,0,0.35);">
                <div class="icon">⚠️</div>
                <div class="bubble-content">Lỗi kết nối: {e}</div>
            </div>
        """, unsafe_allow_html=True)
