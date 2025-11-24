import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS SIÊU CẤP (Final Boss: Liquid + Glass + Apple + No Avatar) ---
st.markdown("""
<style>
    /* 1. NỀN LIQUID (Ảnh chất lỏng) */
    .stApp {
        background-image: url("https://img.freepik.com/free-photo/abstract-black-oil-paint-texture-background_53876-102366.jpg?t=st=1732523000~exp=1732526600~hmac=6c938906103908084700262070402040");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* Lớp phủ tối để chữ dễ đọc */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.6);
        z-index: -1;
    }

    /* 2. XÓA VĨNH VIỄN AVATAR */
    div[data-testid="stChatMessageAvatarBackground"] {
        display: none !important;
    }
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
    }

    /* 3. THIẾT KẾ BONG BÓNG CHAT (GLASS + APPLE GLOW) */
    .stChatMessageContent {
        background: rgba(255, 255, 255, 0.05) !important; /* Kính mờ */
        backdrop-filter: blur(20px);
        border-radius: 20px !important;
        padding: 15px !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        width: fit-content !important;
        max-width: 85%;
        display: inline-block;
    }

    /* --- CĂN CHỈNH TRÁI - PHẢI --- */
    
    /* Tin nhắn của USER (Sếp) -> Sang Phải + Viền Hồng Tím */
    div[data-testid="stChatMessage"]:nth-child(even) {
        flex-direction: row-reverse;
        text-align: right;
    }
    div[data-testid="stChatMessage"]:nth-child(even) .stChatMessageContent {
        margin-left: auto;
        border: 1px solid #FF00FF; /* Viền hồng */
        box-shadow: 0 0 15px rgba(255, 0, 255, 0.4); /* Phát sáng hồng */
    }

    /* Tin nhắn của BOT (Anh Trai) -> Sang Trái + Viền Xanh Neon */
    div[data-testid="stChatMessage"]:nth-child(odd) .stChatMessageContent {
        margin-right: auto;
        border: 1px solid #00FFFF; /* Viền xanh */
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.4); /* Phát sáng xanh */
    }

    /* 4. TIÊU ĐỀ & INPUT */
    h1 {
        text-align: center; 
        color: white;
        text-shadow: 0 0 10px #00FFFF;
    }
    
    .stChatInputContainer textarea {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border: 1px solid #555 !important;
        border-radius: 30px !important;
    }
    
    #MainMenu, footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# --- GIAO DIỆN CHÍNH ---
st.title("😎 Lê Vũ Depzai (Anh Trai)")

# --- 3. CẤU HÌNH API ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa nhập chìa khóa vào két sắt (Secrets)!")

# --- 4. LOGIC BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, lạnh lùng, chiều chuộng. Trả lời ngắn gọn."
    )
    # ĐÂY LÀ DÒNG BỊ LỖI TRƯỚC ĐÓ, GIỜ ĐÃ SỬA:
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. HIỂN THỊ LỊCH SỬ (Ẩn Avatar bằng code) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=None): 
        st.markdown(message["content"])

# --- 6. XỬ LÝ TIN NHẮN ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # User chat
    with st.chat_message("user", avatar=None):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Bot chat
    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        with st.chat_message("assistant", avatar=None):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")