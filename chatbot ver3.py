import streamlit as st
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Lê Vũ Depzai", page_icon="😎", layout="centered")

# --- 2. CSS TÙY CHỈNH GIAO DIỆN (Bản sao y hệt ảnh) ---
st.markdown("""
<style>
    /* --- NỀN LIQUID DARK FULL MÀN HÌNH --- */
    /* Áp dụng cho html, body và .stApp để đảm bảo full màn hình */
    html, body, .stApp {
        height: 100vh; /* Chiều cao 100% view height */
        width: 100vw;  /* Chiều rộng 100% view width */
        margin: 0;
        padding: 0;
        overflow-x: hidden; /* Ẩn thanh cuộn ngang nếu có */
        
        /* Link ảnh nền chất lỏng tối */
        background-image: url("https://sf-static.upanhlaylink.com/img/image_20251124438d8e9e8b4c9f6712b854f513430f8d.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }

    /* Lớp phủ tối để làm nổi bật nội dung */
    .stApp::before {
        content: ""; 
        position: absolute; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 100%;
        background: rgba(0, 0, 0, 0.4); 
        z-index: -1;
        pointer-events: none; /* Đảm bảo lớp phủ không chặn click chuột */
    }

    /* --- CÁC PHẦN CSS KHÁC CỦA BẠN GIỮ NGUYÊN --- */
    /* 2. ẨN GIAO DIỆN CŨ */
    #MainMenu, footer, header {visibility: hidden;}
    .stChatMessageAvatarBackground {display: none !important;} /* Ẩn khung avatar gốc */
    .stChatMessage {background: transparent !important; border: none !important;}

    /* ... (Phần còn lại của CSS từ code gốc của bạn) ... */
    
    /* --- 4. STYLE KHUNG CHAT (ÁP DỤNG CHO CẢ 2) --- */
    .liquid-glass {
        position: relative;
        
        /* Nền kính trong suốt (Đen mờ 5%) */
        background: rgba(0, 0, 0, 0.3); 
        backdrop-filter: blur(0px);
        -webkit-backdrop-filter: blur(0px);
        
        border-radius: 20px;
        padding: 15px 25px;
        margin-bottom: 15px;
        color: #ffffff;
        font-weight: 500;
        display: flex;
        align-items: center;
        z-index: 1;
        max-width: 85%; /* Tăng chiều rộng tối đa một chút cho đẹp hơn */
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* 1. Khai báo biến góc quay (Để màu chạy mượt) */
    @property --angle {
      syntax: '<angle>';
      initial-value: 0deg;
      inherits: false;
    }

    /* 2. Định nghĩa xoay vòng 360 độ */
    @keyframes rainbow-spin {
        to { --angle: 360deg; }
    }

    /* --- VIỀN 7 MÀU XOAY TRÒN LIỀN MẠCH (FULL MÀU) --- */
    .liquid-glass::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 20px; 
        padding: 2px; /* ĐỘ DÀY VIỀN */
        
        /* Dải màu liền mạch (Không có chữ transparent) */
        background: conic-gradient(
            from var(--angle), 
            #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000
        );
        
        /* Tốc độ xoay */
        animation: rainbow-spin 4s linear infinite;
        
        /* Đục lỗ giữa */
        -webkit-mask: 
           linear-gradient(#fff 0 0) content-box, 
           linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        
        pointer-events: none;
        z-index: -1;
        /* --- THÊM DÒNG NÀY ĐỂ VIỀN MỜ ẢO --- */
        filter: blur(2px);
    }

    /* CĂN CHỈNH VỊ TRÍ */
    /* Sếp (User) -> Căn Phải */
    .user-row { 
        display: flex; 
        justify-content: flex-end; 
    }
    .user-row .liquid-glass {
        flex-direction: row-reverse; /* Icon nằm bên phải */
        border-top-right-radius: 5px; /* Góc nhọn */
    }
    .user-row .icon { margin-left: 15px; margin-right: 0; }

    /* Bot (Anh Trai) -> Căn Trái */
    .bot-row { 
        display: flex; 
        justify-content: flex-start; 
    }
    .bot-row .liquid-glass {
        border-top-left-radius: 5px; /* Góc nhọn */
    }
    .bot-row .icon { margin-right: 15px; }


    /* --- KHUNG NHẬP LIỆU (CŨNG 7 MÀU) --- */
    .stChatInputContainer { padding: 20px 0; }
    .stChatInputContainer > div {
        position: relative; border-radius: 30px; padding: 2px;
        background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3);
        background-size: 400%;
        animation: rainbow-run 4s linear infinite;
    }
    .stChatInputContainer textarea {
        border-radius: 28px !important;
        background: rgba(0, 0, 0, 0.6) !important;
        color: white !important; border: none !important;
        backdrop-filter: blur(10px);
    }
    /* Style cho nút gửi (Send icon) */
    .stChatInputContainer button {
        color: rgba(255,255,255,0.8) !important;
    }

    /* TIÊU ĐỀ */
    .title-container { text-align: center; margin-bottom: 30px; }
    .main-title {
        font-size: 2.5rem; font-weight: bold; color: white;
        text-shadow: 0 0 10px rgba(255,255,255,0.5);
    }
    .sub-title { font-size: 1rem; color: rgba(255,255,255,0.7); }
</style>
""", unsafe_allow_html=True)

# ... (Phần còn lại của code Python giữ nguyên) ...