import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Le Vu AI", page_icon="", layout="centered")

# --- 2. CSS SIÊU CẤP (KÍNH TÀNG HÌNH + XOAY LIỀN MẠCH) ---
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
        background: rgba(0, 0, 0, 0.2); /* Nền tối nhẹ */
        z-index: -1; pointer-events: none;
    }
/* --- VIỀN SƯƠNG MÙ 7 MÀU (FOGGY RAINBOW) --- */
    
    /* LỚP 1: LÕI SƯƠNG (Đậm hơn, sát mép) */
    body::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: 9999;
        pointer-events: none;
        
        /* Tăng độ dày lên để sương có độ "đầm" */
        padding: 10px; 
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: spin 4s linear infinite;
        
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        
        /* ĐÂY LÀ CHÌA KHÓA: Làm nhòe mạnh ngay từ lớp chính */
        filter: blur(15px); 
        opacity: 0.8;
    }
    
    /* LỚP 2: HƠI SƯƠNG LAN TỎA (Nhạt hơn, loe rộng) */
    body::after {
        content: "";
        position: fixed;
        /* Loe rộng ra ngoài màn hình rất nhiều */
        top: -30px; left: -30px; right: -30px; bottom: -30px;
        z-index: 9998;
        pointer-events: none;
        
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        animation: spin 4s linear infinite;
        
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;

        /* Blur cực mạnh để tạo cảm giác như khói/sương */
        filter: blur(50px); 
        opacity: 0.5;
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

    /* --- KHUNG CHAT SIÊU TRONG SUỐT (ULTRA CLEAR) --- */
    .liquid-glass {
        position: relative;
        
        /* CHỈNH ĐỘ TRONG Ở ĐÂY: Để 0.01 là gần như tàng hình */
        background: rgba(255, 255, 255, 0.01); 
        
        /* Blur nhẹ hơn để nhìn rõ nền */
        backdrop-filter: blur(2px); 
        -webkit-backdrop-filter: blur(2px);
        
        border-radius: 35px;
        padding: 12px 25px;
        margin-bottom: 15px;
        color: white;
        font-weight: 500;
        display: flex; align-items: center;
        z-index: 1;
        
        /* Viền kính siêu mỏng */
        border: 1px solid rgba(255,255,255,0.05);
        
        width: fit-content; max-width: 85%;
    }

    /* --- VIỀN 7 MÀU XOAY LIỀN MẠCH (KHÔNG NGẮT QUÃNG) --- */
    .liquid-glass::before {
        content: "";
        position: absolute;
        inset: 0; /* Phủ kín khung */
        z-index: -1;
        border-radius: 35px; 
        padding: 2px; /* ĐỘ DÀY VIỀN */
        
        /* Dải màu LIỀN MẠCH (Full Circle) */
        /* Quan trọng: Màu đầu (#00C6FF) và màu cuối (#00C6FF) PHẢI GIỐNG NHAU để xoay không bị giật */
        background: conic-gradient(
            from var(--angle), 
            #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00, #E0C3FC, #00C6FF
        );
        
        animation: spin 6s linear infinite; /* Xoay đều 4 giây 1 vòng */
        
        /* Kỹ thuật Mask: Chỉ hiện viền */
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        
        /* Glow nhẹ */
        filter: blur(10px);
    }
    
    /* Lớp Glow loe sáng bên ngoài */
    .liquid-glass::after {
        content: "";
        position: absolute;
        inset: -4px;
        z-index: -4;
        border-radius: 35px;
        background: conic-gradient(
            from var(--angle), 
            #00C6FF, #0072FF, #8E2DE2, #F80759, #FF8C00, #E0C3FC, #00C6FF
        );
        animation: spin 4s linear infinite;
        filter: blur(20px); /* Độ loe sáng */
        opacity: 0.7;
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
        /* Cũng xoay liền mạch luôn */
        background: conic-gradient(from var(--angle), #00C6FF, #8E2DE2, #F80759, #FF8C00, #00C6FF);
        animation: spin 4s linear infinite;
        box-shadow: 0 0 20px rgba(0, 198, 255, 0.2);
    }
    .stChatInputContainer textarea {
        border-radius: 33px !important;
        background: rgba(0, 0, 0, 0.3) !important; /* Input cũng trong hơn */
        color: white !important; border: none !important;
        backdrop-filter: blur(15px);
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