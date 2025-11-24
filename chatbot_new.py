import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS TÙY CHỈNH GIAO DIỆN (Bản sao y hệt ảnh) ---
st.markdown("""
<style>
    /* --- NỀN LIQUID DARK --- */
    .stApp {
        /* Link ảnh nền chất lỏng tối */
        background-image: url("https://www.freepik.com/free-photo/marbled-blue-abstract-background-liquid-marble-pattern_26435892.htm#fromView=image_search&page=1&position=6&uuid=a1c9367a-3035-4104-a595-eedad14fbfd8");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    /* Lớp phủ tối để làm nổi bật nội dung */
    .stApp::before {
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.4); z-index: -1;
    }

    /* --- ẨN CÁC THÀNH PHẦN MẶC ĐỊNH KHÔNG CẦN THIẾT --- */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;} /* Ẩn khung avatar gốc */

    /* --- STYLE CHUNG CHO CÁC KHUNG "LIQUID GLASS" --- */
    .liquid-glass {
        backdrop-filter: blur(15px); /* Hiệu ứng kính mờ */
        -webkit-backdrop-filter: blur(15px);
        background: rgba(255, 255, 255, 0.08); /* Nền kính trong suốt nhẹ */
        border-radius: 20px;
        padding: 15px 20px;
        margin-bottom: 15px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        box-shadow: inset 0 0 15px rgba(255,255,255,0.05); /* Bóng kính bên trong */
        border: 2px solid transparent; /* Viền trong suốt để chuẩn bị cho màu */
    }
    .liquid-glass .icon {
        margin-right: 15px;
        font-size: 1.5rem;
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));
    }

    /* --- KHUNG CHAT CỦA SẾP (User) - MÀU ĐỎ --- */
    .user-bubble {
        border-color: rgba(255, 50, 50, 0.7) !important; /* Viền đỏ */
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.4), inset 0 0 10px rgba(255, 0, 0, 0.2) !important; /* Phát sáng đỏ */
        background: linear-gradient(135deg, rgba(255,50,50,0.1), rgba(0,0,0,0)) !important;
    }

    /* --- KHUNG CHAT CỦA BOT (Anh Trai) - MÀU VÀNG CAM --- */
    .bot-bubble {
        border-color: rgba(255, 180, 0, 0.7) !important; /* Viền vàng cam */
        box-shadow: 0 0 20px rgba(255, 160, 0, 0.4), inset 0 0 10px rgba(255, 160, 0, 0.2) !important; /* Phát sáng vàng */
        background: linear-gradient(135deg, rgba(255,180,0,0.1), rgba(0,0,0,0)) !important;
    }

    /* --- KHUNG NHẬP LIỆU - VIỀN CẦU VỒNG (RAINBOW) --- */
    .stChatInputContainer {
        padding: 20px 0;
    }
    .stChatInputContainer > div {
        position: relative;
        border-radius: 30px;
        padding: 2px; /* Độ dày viền cầu vồng */
        /* Tạo gradient cầu vồng */
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3); /* Phát sáng nhẹ */
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important;
        background: rgba(0, 0, 0, 0.6) !important; /* Nền tối bên trong */
        color: white !important;
        border: none !important;
        padding: 15px 20px !important;
        backdrop-filter: blur(10px);
    }
    /* Style cho nút gửi (Send icon) */
    .stChatInputContainer button {
        color: rgba(255,255,255,0.8) !important;
    }

    /* --- TIÊU ĐỀ & SUBTITLE --- */
    .title-container {
        text-align: center; margin-bottom: 30px;
    }
    .main-title {
        font-size: 2.5rem; font-weight: bold; color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.3);
    }
    .sub-title {
        font-size: 1rem; color: rgba(255,255,255,0.7);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. GIAO DIỆN TIÊU ĐỀ ---
st.markdown("""
    <div class="title-container">
        <div class="main-title">😎 Lê Vũ Depzai (Anh Trai)</div>
        <div class="sub-title">Trò chuyện cùng anh Lê Vũ</div>
    </div>
""", unsafe_allow_html=True)

# --- 4. CẤU HÌNH API (BẢO MẬT) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"] # Đảm bảo tên này khớp với trong Secrets của Sếp
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Chưa có chìa khóa! Hãy vào Settings -> Secrets để điền API Key.")
    st.stop()

# --- 5. KHỞI TẠO BOT ---
if "chat_session" not in st.session_state:
    model = genai.GenerativeModel(
        'models/gemini-2.0-flash',
        system_instruction="Bạn tên là 'Lê Vũ depzai'. Bạn là anh trai, gọi người dùng là 'em'. Phong cách: Ngầu, quan tâm, ngắn gọn, trưởng thành."
    )
    st.session_state.chat_session = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. HIỂN THỊ LỊCH SỬ CHAT (Dùng HTML tùy chỉnh để giống ảnh) ---
for message in st.session_state.messages:
    if message["role"] == "user":
        # Tin nhắn của Sếp: Icon mặt đỏ + Viền đỏ
        st.markdown(f"""
            <div class="liquid-glass user-bubble">
                <span class="icon">🔴</span> {message["content"]}
            </div>
        """, unsafe_allow_html=True)
    else:
        # Tin nhắn của Bot: Icon robot vàng + Viền vàng
        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <span class="icon">🤖</span> {message["content"]}
            </div>
        """, unsafe_allow_html=True)

# --- 7. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # 7.1. Hiển thị tin nhắn User ngay lập tức
    st.markdown(f"""
        <div class="liquid-glass user-bubble">
            <span class="icon">🔴</span>
            {user_input}
        </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 7.2. Gửi cho AI và nhận phản hồi
    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text
        
        # 7.3. Hiển thị tin nhắn Bot
        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <span class="icon">🤖</span>
                {bot_reply}
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    except Exception as e:
        # Hiển thị lỗi trong khung kính đỏ
        st.markdown(f"""
            <div class="liquid-glass user-bubble" style="border-color: red;">
                <span class="icon">⚠️</span> Lỗi kết nối: {e}
            </div>
        """, unsafe_allow_html=True)