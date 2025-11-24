import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (FIX LỖI LAYOUT + GIAO DIỆN KÍNH) ---
st.markdown("""
<style>
    /* --- NỀN LIQUID FULL MÀN HÌNH --- */
    [data-testid="stAppViewContainer"] {
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    [data-testid="stAppViewContainer"]::before {
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.3); z-index: -1; pointer-events: none;
    }

    /* --- ẨN GIAO DIỆN CŨ --- */
    #MainMenu, footer {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;}
    .stChatMessage {background: transparent !important; border: none !important;}

    /* --- ANIMATION VIỀN CHẠY --- */
    @property --angle { syntax: '<angle>'; initial-value: 0deg; inherits: false; }
    @keyframes rainbow-spin { to { --angle: 360deg; } }

    /* --- STYLE KHUNG CHAT (LIQUID GLASS) --- */
    .liquid-glass {
        position: relative;
        background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border-radius: 25px;
        padding: 12px 20px;
        color: #ffffff; font-weight: 500;
        display: flex; align-items: center;
        z-index: 1;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        width: fit-content; max-width: 80%;
    }

    /* Viền 7 màu chạy */
    .liquid-glass::before {
        content: ""; position: absolute; inset: 0; border-radius: 25px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        pointer-events: none; z-index: -1; filter: blur(2px);
    }

    .icon { margin-right: 12px; font-size: 1.6rem; }
    
    /* --- FIX LỖI CĂN CHỈNH (QUAN TRỌNG) --- */
    /* Bắt buộc hàng chứa chat phải rộng 100% để đẩy sang 2 bên được */
    .user-row { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 15px; }
    .bot-row { display: flex; justify-content: flex-start; width: 100%; margin-bottom: 15px; }

    /* --- STYLE KHUNG TẢI ẢNH (LÀM ĐẸP LẠI) --- */
    [data-testid="stFileUploader"] {
        width: 100%;
        padding: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 10px;
    }
    /* Ẩn bớt chữ thừa của uploader */
    [data-testid="stFileUploader"] section { padding: 0; }
    [data-testid="stFileUploader"] button { display: none; } /* Ẩn nút browse xấu xí mặc định nếu muốn */

    /* --- KHUNG INPUT --- */
    .stChatInputContainer { padding-bottom: 30px; }
    .stChatInputContainer > div {
        position: relative; border-radius: 30px; padding: 2px;
        background: conic-gradient(from var(--angle), #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000);
        animation: rainbow-spin 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important; background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important; backdrop-filter: blur(10px);
    }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 20px; margin-top: -30px; }
    .main-title { font-size: 2.2rem; font-weight: 800; color: white; text-shadow: 0 0 15px rgba(255,255,255,0.4); }
    .sub-title { font-size: 0.9rem; color: rgba(255,255,255,0.8); }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">😎 Lê Vũ Depzai</div>
        <div class="sub-title">Trò chuyện & Phân tích ảnh</div>
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
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, ngắn gọn. Nếu có ảnh, hãy nhận xét ảnh."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. KHUNG CHAT HISTORY ---
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
            <div class="user-row">
                <div class="liquid-glass">
                    <span class="icon">🔴</span> <div>{message["content"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass">
                    <span class="icon">🤖</span> <div>{message["content"]}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. KHUNG NHẬP LIỆU VÀ ẢNH ---
# Tạo một container bên dưới để chứa phần upload và input
with st.container():
    # Nút mở rộng để upload ảnh (cho gọn)
    with st.expander("📸 Gửi ảnh (Bấm để mở)"):
        uploaded_file = st.file_uploader("Chọn ảnh", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        image_to_send = None
        if uploaded_file:
            image_to_send = Image.open(uploaded_file)
            st.image(image_to_send, caption="Ảnh đã chọn", width=150)
            
    # Input chat
    user_input = st.chat_input("Nói gì với anh đi em...")

# --- 8. XỬ LÝ LOGIC ---
# Nút gửi ảnh chỉ hiện khi đã chọn ảnh
send_clicked = False
if image_to_send and not user_input:
    send_clicked = st.button("Gửi ảnh ngay")

if user_input or (image_to_send and send_clicked):
    
    display_text = user_input if user_input else "[Đã gửi một hình ảnh]"
    
    # 1. Hiện User Bubble
    st.markdown(f"""
        <div class="user-row">
            <div class="liquid-glass">
                <span class="icon">🔴</span> <div>{display_text}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Hiện ảnh nếu có
    if image_to_send:
        with st.chat_message("user", avatar=None): # Dùng container gốc để hiện ảnh cho đẹp
            st.image(image_to_send, width=300)

    st.session_state.messages.append({"role": "user", "content": display_text})

    # 3. Gửi Gemini
    try:
        inputs = []
        if user_input: inputs.append(user_input)
        else: inputs.append("Hãy nhận xét bức ảnh này.")
        
        if image_to_send: inputs.append(image_to_send)

        with st.spinner("Đang xử lý..."):
            response = st.session_state.chat_session.send_message(inputs)
            bot_reply = response.text
        
        # 4. Hiện Bot Bubble
        st.markdown(f"""
            <div class="bot-row">
                <div class="liquid-glass">
                    <span class="icon">🤖</span> <div>{bot_reply}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi: {e}")