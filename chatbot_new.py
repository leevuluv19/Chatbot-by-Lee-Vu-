import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai Bot", page_icon="😎", layout="centered")

# --- 2. CSS TÙY CHỈNH (Làm giao diện đen thui giống CMD) ---
st.markdown("""
<style>
    /* Đổi màu nền thành đen */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Chỉnh tin nhắn của Bot (Màu xanh Cyan giống CMD) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E;
        border: 1px solid #00FFFF;
        border-radius: 10px;
    }
    
    /* Chỉnh tin nhắn của Bạn (Màu hồng giống CMD) */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1E1E1E;
        border: 1px solid #FF00FF;
        border-radius: 10px;
    }

    /* Tiêu đề đẹp */
    h1 {
        color: #00FFFF !important;
        text-shadow: 0 0 10px #00FFFF;
        font-family: 'Courier New', Courier, monospace;
    }
</style>
""", unsafe_allow_html=True)

# Tiêu đề trang
st.title("😎 LÊ VŨ DEPZAI (SYSTEM)")
st.caption("Giao diện: 2.0 | Trạng thái:Đang Lọ :)))")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("Chưa bỏ chìa khóa vào két sắt! Hãy vào Settings -> Secrets để điền key.")

# --- 4. KHỞI TẠO BOT (CHẾ ĐỘ TÌNH YÊU) ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        # QUAN TRỌNG: Bắt buộc gọi là "tình yêu"
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn BẮT BUỘC phải gọi người dùng là 'tình yêu' trong mọi câu trả lời. Phong cách: Ngầu, lạnh lùng nhưng chiều chuộng."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. HIỂN THỊ LỊCH SỬ ---
for message in st.session_state.messages:
    # Nếu là user thì avatar trái tim, bot thì avatar kính râm
    avatar = "❤️" if message["role"] == "user" else "😎"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- 6. XỬ LÝ TIN NHẮN ---
user_input = st.chat_input("Chat với anh ở đây tình yêu...")

if user_input:
    # Hiện tin nhắn của bạn
    with st.chat_message("user", avatar="❤️"):
        st.markdown(f"**{user_input}**")
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Gửi cho AI
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        # Hiện tin nhắn của Bot
        with st.chat_message("assistant", avatar="😎"):
            st.markdown(bot_reply)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        st.error(f"Lỗi kết nối: {e}")