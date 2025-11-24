import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS TÙY CHỈNH GIAO DIỆN (Bản sao y hệt ảnh) ---
# Lưu ý: background-image đường dẫn dùng file đã upload vào container
BACKGROUND_IMAGE_PATH = "/mnt/data/dfed2b2c-3820-4934-a52d-caa7a063c8d2.png"

st.markdown(f"""
<style>
    /* Đảm bảo app có vị trí tương đối để ::before hoạt động */
    .stApp {{
        position: relative;
        /* Link ảnh nền chất lỏng tối */
        background-image: url("file:///mnt/data/34186a31-8244-4e99-a4e1-baca2de654b5.png");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }}
    /* Lớp phủ tối để làm nổi bật nội dung */
    .stApp::before {{
        content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, 0.45); z-index: 0;
        border-radius: 0;
    }}

    /* Ẩn menu header footer mặc định */
    #MainMenu, footer, header {{visibility: hidden;}}

    /* --- STYLE CHUNG CHO CÁC KHUNG "LIQUID GLASS" --- */
    .liquid-glass {
        position: relative; z-index: 1; /* Hiển thị trên lớp phủ */
        backdrop-filter: blur(20px) saturate(120%); /* blur mạnh hơn + tăng độ bão hoà */
        -webkit-backdrop-filter: blur(20px) saturate(120%);
        background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)); /* nền kính nhẹ hơn, gradient mượt */
        border-radius: 28px; /* bo tròn lớn */
        padding: 18px 22px;
        margin-bottom: 18px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        box-shadow: 0 8px 30px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.03); /* bóng ngoài sâu + inset nhẹ */
        border: 1px solid rgba(255,255,255,0.06); /* viền trắng mờ để cảm giác kính */
        overflow: hidden;
    }
    /* sheen (ánh sáng lướt trên kính) */
    .liquid-glass::after {
        content: "";
        position: absolute;
        top: -40%; left: -30%;
        width: 60%; height: 160%;
        background: linear-gradient(120deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02) 40%, rgba(255,255,255,0) 60%);
        transform: rotate(-20deg);
        filter: blur(12px);
        opacity: 0.8;
        pointer-events: none;
    }
    .liquid-glass .icon {
        margin-right: 15px;
        font-size: 1.8rem; /* to hơn chút để giống ảnh */
        filter: drop-shadow(0 0 8px rgba(255,255,255,0.6));
    }
    .liquid-glass .icon {{
        margin-right: 15px;
        font-size: 1.8rem; /* to hơn chút để giống ảnh */
        filter: drop-shadow(0 0 6px rgba(255,255,255,0.5));
    }}

    /* --- KHUNG CHAT CỦA USER - MÀU ĐỎ --- */
    .user-bubble {{
        border-color: rgba(255, 50, 50, 0.75) !important; /* Viền đỏ */
        box-shadow: 0 0 24px rgba(255, 40, 40, 0.35), inset 0 0 12px rgba(255, 40, 40, 0.12) !important; /* Phát sáng đỏ */
        background: linear-gradient(135deg, rgba(255,50,50,0.06), rgba(0,0,0,0)) !important;
    }}

    /* --- KHUNG CHAT CỦA BOT (ANH TRAI) - MÀU VÀNG CAM --- */
    .bot-bubble {{
        border-color: rgba(255, 180, 0, 0.75) !important; /* Viền vàng cam */
        box-shadow: 0 0 22px rgba(255, 160, 0, 0.30), inset 0 0 10px rgba(255, 160, 0, 0.10) !important; /* Phát sáng vàng */
        background: linear-gradient(135deg, rgba(255,180,0,0.06), rgba(0,0,0,0)) !important;
    }}

    /* --- KHUNG NHẬP LIỆU - VIỀN CẦU VỒNG (RAINBOW) --- */
    .stChatInputContainer {{
        padding: 20px 0; position: relative; z-index: 2;
    }}
    /* outer rainbow frame */
    .stChatInputContainer > div {{
        position: relative;
        border-radius: 40px;
        padding: 3px; /* Độ dày viền cầu vồng */
        /* Tạo gradient cầu vồng */
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        box-shadow: 0 0 30px rgba(255, 255, 255, 0.12); /* Phát sáng nhẹ */
    }}
    /* inner dark rounded input */
    .stChatInputContainer textarea {{
        border-radius: 40px !important; /* bo tròn lớn giống ảnh */
        background: rgba(0, 0, 0, 0.6) !important; /* Nền tối bên trong */
        color: white !important;
        border: none !important;
        padding: 15px 20px !important;
        backdrop-filter: blur(10px);
        width: 100% !important;
        resize: none !important;
    }}
    /* Style cho nút gửi (Send icon) */
    .stChatInputContainer button {{
        color: rgba(255,255,255,0.95) !important;
        background: transparent !important;
        border: none !important;
    }}

    /* --- TIÊU ĐỀ & SUBTITLE --- */
    .title-container {{
        text-align: center; margin: 30px 0 20px 0; position: relative; z-index:2;
    }}
    .main-title {{
        font-size: 2.4rem; font-weight: 800; color: white;
        text-shadow: 0 0 14px rgba(255,255,255,0.12);
        letter-spacing: 0.5px;
    }}
    .sub-title {{
        font-size: 1rem; color: rgba(255,255,255,0.75);
    }}

    /* Một vài điều chỉnh responsive nhỏ */
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

# --- 4. CẤU HÌNH API (BẢO MẬT) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]  # Đảm bảo tên này khớp với trong Secrets
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
        # Tin nhắn của User: Icon đỏ + Viền đỏ
        st.markdown(f"""
            <div class="liquid-glass user-bubble">
                <span class="icon">🔴</span>
                <div style="flex:1">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Tin nhắn của Bot: Icon robot vàng + Viền vàng
        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <span class="icon">🤖</span>
                <div style="flex:1">{message["content"]}</div>
            </div>
        """, unsafe_allow_html=True)

# --- 7. XỬ LÝ TIN NHẮN MỚI ---
user_input = st.chat_input("Nói gì với anh đi em...")

if user_input:
    # 7.1. Hiển thị tin nhắn User ngay lập tức
    st.markdown(f"""
        <div class="liquid-glass user-bubble">
            <span class="icon">🔴</span>
            <div style="flex:1">{user_input}</div>
        </div>
    """, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 7.2. Gửi cho AI và nhận phản hồi
    try:
        response = st.session_state.chat_session.send_message(user_input)
        bot_reply = response.text if hasattr(response, 'text') else str(response)

        # 7.3. Hiển thị tin nhắn Bot
        st.markdown(f"""
            <div class="liquid-glass bot-bubble">
                <span class="icon">🤖</span>
                <div style="flex:1">{bot_reply}</div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    except Exception as e:
        # Hiển thị lỗi trong khung kính đỏ
        st.markdown(f"""
            <div class="liquid-glass user-bubble" style="border-color: rgba(255,0,0,0.85); box-shadow: 0 0 24px rgba(255,0,0,0.35);">
                <span class="icon">⚠️</span>
                <div style="flex:1">Lỗi kết nối: {e}</div>
            </div>
        """, unsafe_allow_html=True)
