import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai (Anh Trai)", page_icon="😎", layout="centered")

# --- 2. CSS TÙY CHỈNH GIAO DIỆN (QUAN TRỌNG) ---
st.markdown("""
<style>
    /* --- NỀN TRANG WEB --- */
    .stApp {
        background-color: #1E1E1E; /* Màu nền tối giống trong ảnh */
        color: #FFFFFF; /* Chữ màu trắng */
    }

    /* --- TIÊU ĐỀ --- */
    h1 {
        text-align: center;
        font-weight: bold;
        padding-bottom: 20px;
    }
    
    /* --- ẨN AVATAR MẶC ĐỊNH --- */
    .stChatMessage .stChatMessageAvatarBackground {
        display: none;
    }

    /* --- TÙY CHỈNH CHAT BUBBLE CHUNG --- */
    .stChatMessage {
        background-color: transparent !important; /* Ẩn nền mặc định */
        border: none !important; /* Ẩn viền mặc định */
    }
    
    .stChatMessageContent {
        padding: 15px;
        border-radius: 20px;
        max-width: 80%; /* Chiều rộng tối đa của bubble */
        color: #FFFFFF;
    }

    /* --- CHAT BUBBLE CỦA USER (Sếp) - MÀU ĐỎ, CĂN PHẢI --- */
    /* Streamlit sắp xếp tin nhắn theo thứ tự, User thường là số chẵn (2, 4, 6...) */
    div[data-testid="stChatMessage"]:nth-child(even) {
        flex-direction: row-reverse; /* Đảo chiều để căn phải */
    }
    
    div[data-testid="stChatMessage"]:nth-child(even) .stChatMessageContent {
        background-color: #2C2C2E; /* Nền tối cho bubble */
        border: 2px solid #FF3B30; /* Viền màu ĐỎ */
        border-top-right-radius: 5px; /* Tạo góc nhọn bên phải */
        margin-left: auto; /* Đẩy sang phải */
    }

    /* --- CHAT BUBBLE CỦA BOT (Anh Trai) - MÀU VÀNG, CĂN TRÁI --- */
    /* Bot thường là số lẻ (1, 3, 5...) */
    div[data-testid="stChatMessage"]:nth-child(odd) .stChatMessageContent {
        background-color: #2C2C2E; /* Nền tối cho bubble */
        border: 2px solid #FFCC00; /* Viền màu VÀNG/GOLD */
        border-top-left-radius: 5px; /* Tạo góc nhọn bên trái */
        margin-right: auto; /* Đẩy sang trái */
    }

    /* --- KHUNG NHẬP LIỆU --- */
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    .stChatInputContainer textarea {
        background-color: #2C2C2E !important;
        color: #FFFFFF !important;
        border: 1px solid #555555 !important;
        border-radius: 30px !important;
    }
    
</style>
""", unsafe_allow_html=True)

# --- TIÊU ĐỀ CHÍNH ---
st.title("Lê Vũ Depzai (Anh Trai)")
st.caption("Trò chuyện cùng anh Lê Vũ")

# --- 3. CẤU HÌNH API ---
try:
    # Nhớ thay tên két sắt nếu Sếp đặt tên khác
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có chìa khóa! Hãy vào Settings -> Secrets để điền API Key.")
    st.stop()

# --- 4. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        # Cài đặt tính cách: Xưng Anh - Gọi Em
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai của người dùng. Hãy xưng là 'anh' và gọi người dùng là 'em'. Phong cách nói chuyện: Ngầu, quan tâm, ngắn gọn, trưởng thành."
    )
    st.session_state.chat_session = model.start_chat(history=[])

# --- 5. QUẢN LÝ LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    # avatar=None để ẩn icon
    with st.chat_message(message["role"], avatar=None):
        st.markdown(message["content"])

# --- 6. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # 6.1. Hiển thị tin nhắn của User
    with st.chat_message("user", avatar=None):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 6.2. Gửi cho AI và nhận phản hồi
    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        # 6.3. Hiển thị tin nhắn của Bot
        with st.chat_message("assistant", avatar=None):
            st.markdown(bot_reply)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")