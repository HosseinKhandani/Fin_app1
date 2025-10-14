import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities.hasher import Hasher
import json
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from google import genai
from google.genai import types
import os
import tempfile
import zipfile
from collections import deque
from itertools import cycle
import time
import re
from typing import List, Dict, Any, Tuple
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="AI Financial Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

proxy_url = "http://185.173.168.31:22525"
os.environ['HTTP_PROXY'] = proxy_url
os.environ['HTTPS_PROXY'] = proxy_url

api_keys = []

# ==================== AUTHENTICATION CODE START ====================

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

hashed_passwords = stauth.Hasher(["elnagh", "abc_fin_cba","123"]).generate()

config['credentials']['usernames']['admin']['password'] = hashed_passwords[0]
config['credentials']['usernames']['fin.analyst']['password'] = hashed_passwords[1]
config['credentials']['usernames']['h.khandani']['password'] = hashed_passwords[2]

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None

if st.session_state.authentication_status is None:
    name, authentication_status, username = authenticator.login(location='main')
    st.session_state.authentication_status = authentication_status
    st.session_state.name = name
    st.session_state.username = username

if st.session_state.authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()

if st.session_state.authentication_status == None:
    st.warning('Please enter your username and password')
    st.stop()

# If authenticated, show the main app
if st.session_state.authentication_status:
    
    # ==================== CUSTOM SIDEBAR ====================
    
    with st.sidebar:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
            <h2 style="color: white; margin: 0; font-size: 1.3rem;">👋 خوش آمدید</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 600;">{st.session_state.name}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); margin-bottom: 2rem; border-right: 4px solid #667eea;">
            <h3 style="color: #2C3E50; margin-bottom: 1rem; font-size: 1.2rem;">📋 راهنمای سریع</h3>
            <div style="color: #7F8C8D; font-size: 0.9rem; line-height: 1.8;">
                <p style="margin: 0.5rem 0;"><strong>🔹 گام اول:</strong> فایل‌های PDF را بارگذاری کنید</p>
                <p style="margin: 0.5rem 0;"><strong>🔹 گام دوم:</strong> تحلیل هوشمند را آغاز کنید</p>
                <p style="margin: 0.5rem 0;"><strong>🔹 گام سوم:</strong> نتایج را مشاهده و دانلود کنید</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <p style="color: white; margin: 0; font-size: 0.85rem; text-align: center;">💡 <strong>نکته:</strong> فایل‌ها باید با کیفیت بالا باشند</p>
        </div>
        """, unsafe_allow_html=True)
        
        authenticator.logout('🚪 خروج از سیستم', 'sidebar')
    
    # ==================== ENHANCED CSS WITH MODERN DESIGN ====================
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'B Mitra', 'Tahoma', sans-serif !important;
            direction: rtl !important;
            text-align: right !important;
        }
        
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            direction: rtl;
            padding: 2rem 1rem;
        }
        
        .stApp {
            background: transparent;
            direction: rtl;
        }
        
        /* ==================== TABS STYLING ==================== */
        
        .stTabs {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 0.5rem;
            direction: rtl;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background: transparent;
            border-radius: 12px;
            color: #6c757d;
            font-size: 1.1rem;
            font-weight: 600;
            padding: 0 2rem;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        /* ==================== HEADER STYLING ==================== */
        
        .main-header {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #f5576c);
        }
        
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            text-align: center;
        }
        
        .main-subtitle {
            color: #6c757d;
            font-size: 1.1rem;
            margin-top: 0.5rem;
            text-align: center;
        }
        
        /* ==================== ALERT BOXES ==================== */
        
        .alert-box {
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-right: 5px solid;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            animation: slideIn 0.5s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .alert-info {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-right-color: #2196f3;
        }
        
        .alert-success {
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-right-color: #4caf50;
        }
        
        .alert-warning {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-right-color: #ff9800;
        }
        
        .alert-danger {
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
            border-right-color: #f44336;
        }
        
        .alert-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .alert-content {
            color: #424242;
            line-height: 1.8;
            font-size: 1rem;
        }
        
        /* ==================== METRIC CARDS ==================== */
        
        .modern-metric {
            background: white;
            border-radius: 18px;
            padding: 1.8rem;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .modern-metric::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--gradient-start), var(--gradient-end));
        }
        
        .modern-metric:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.12);
        }
        
        .metric-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .metric-label {
            color: #6c757d;
            font-size: 1rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* ==================== FILE UPLOAD AREA ==================== */
        
        .upload-zone {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border: 3px dashed #667eea;
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            margin: 2rem 0;
        }
        
        .upload-zone:hover {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-color: #764ba2;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            animation: bounce 2s infinite;
        }
        
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .upload-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .upload-subtitle {
            color: #6c757d;
            font-size: 1rem;
        }
        
        /* ==================== FILE LIST ==================== */
        
        .file-card {
            background: white;
            border-radius: 12px;
            padding: 1.2rem;
            margin: 0.8rem 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
            border-right: 4px solid #667eea;
        }
        
        .file-card:hover {
            box-shadow: 0 6px 20px rgba(0,0,0,0.1);
            transform: translateX(-5px);
        }
        
        .file-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .file-icon {
            font-size: 2rem;
        }
        
        .file-name {
            font-weight: 600;
            color: #2c3e50;
            font-size: 1.05rem;
        }
        
        .file-size {
            color: #6c757d;
            font-size: 0.9rem;
        }
        
        .file-status {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
        }
        
        .status-ready {
            background: linear-gradient(135deg, #4caf50, #66bb6a);
            color: white;
        }
        
        /* ==================== BUTTONS ==================== */
        
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 1rem 2.5rem;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stButton > button:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        }
        
        /* ==================== PROGRESS BAR ==================== */
        
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
            border-radius: 10px;
        }
        
        /* ==================== RESULTS CARD ==================== */
        
        .result-card {
            background: white;
            border-radius: 18px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.08);
            border-top: 5px solid;
            transition: all 0.3s ease;
        }
        
        .result-card:hover {
            box-shadow: 0 12px 35px rgba(0,0,0,0.12);
            transform: translateY(-3px);
        }
        
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f1f3f5;
        }
        
        .result-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #2c3e50;
        }
        
        .risk-badge {
            padding: 0.6rem 1.5rem;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .risk-low {
            background: linear-gradient(135deg, #4caf50, #66bb6a);
            color: white;
        }
        
        .risk-medium {
            background: linear-gradient(135deg, #ff9800, #ffa726);
            color: white;
        }
        
        .risk-high {
            background: linear-gradient(135deg, #ff5722, #ff7043);
            color: white;
        }
        
        .risk-critical {
            background: linear-gradient(135deg, #f44336, #e57373);
            color: white;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .info-item {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 2px solid #e9ecef;
        }
        
        .info-label {
            color: #6c757d;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }
        
        .info-value {
            color: #2c3e50;
            font-size: 1.1rem;
            font-weight: 700;
        }
        
        /* ==================== NAVIGATION HELPER ==================== */
        
        .nav-helper {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        .nav-helper-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .nav-helper-text {
            font-size: 1rem;
            opacity: 0.95;
        }
        
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* RTL Fixes */
        .stFileUploader > div {
            direction: rtl !important;
        }
        
        .stSelectbox label, .stRadio label {
            direction: rtl !important;
            text-align: right !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # ==================== API & ANALYZER SETUP ====================

    api_key_cycler = cycle(api_keys)

    def get_client():
        api_key = next(api_key_cycler)
        return genai.Client(api_key=api_key)

    class FinancialAnalyzer:
        def __init__(self):
            self.response_schema = {
                "type": "object",
                "properties": {
                    "تحلیل_جامع_گزارش_حسابرسی": {
                        "type": "object",
                        "properties": {
                            "بخش۱_خلاصه_و_اطلاعات_کلیدی": {
                                "type": "object",
                                "properties": {
                                    "نام_شرکت": {"type": "string"},
                                    "نام_حسابرس": {"type": "string"},
                                    "دوره_مالی": {"type": "string"},
                                    "نوع_اظهارنظر": {
                                        "type": "string",
                                        "enum": ["مقبول", "مشروط", "مردود", "عدم اظهارنظر"]
                                    },
                                    "سطح_ریسک_کلی_بنا_به_نظر_بازرس": {
                                        "type": "string",
                                        "enum": ["پایین", "متوسط", "بالا", "بحرانی"]
                                    },
                                    "سطح_ریسک_کلی_بنا_به_نظر_مدل_زبانی": {
                                        "type": "string",
                                        "enum": ["پایین", "متوسط", "بالا", "بحرانی"]
                                    },
                                    "جزییات_سطح_ریسک_تعیین_شده_توسط_مدل": {"type": "string"},
                                    "نکات_کلیدی_و_نتیجه_گیری": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    }
                                },
                                "required": ["نام_شرکت", "نام_حسابرس", "دوره_مالی", "نوع_اظهارنظر", 
                                           "سطح_ریسک_کلی_بنا_به_نظر_بازرس", "سطح_ریسک_کلی_بنا_به_نظر_مدل_زبانی",
                                           "جزییات_سطح_ریسک_تعیین_شده_توسط_مدل", "نکات_کلیدی_و_نتیجه_گیری"]
                            }
                        }
                    }
                },
                "required": ["تحلیل_جامع_گزارش_حسابرسی"]
            }
        
        def extract_table_from_page(self, file_content):
            client = get_client()
            prompt = """لطفاً گزارش حسابرسی را تحلیل کنید."""
            
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    types.Part.from_bytes(data=file_content, mime_type="application/pdf"),
                    prompt
                ],
                config={
                    'system_instruction': """شما یک تحلیلگر مالی خبره هستید.""",
                    "response_mime_type": "application/json",
                    "response_schema": self.response_schema,
                    "temperature": 0.5
                }
            )
            
            return json.loads(response.text)

    # ==================== HELPER FUNCTIONS ====================
    
    def flatten_reference_data(df):
        if 'ارجاع' in df.columns:
            df['شماره_بند'] = df['ارجاع'].apply(
                lambda x: x.get('شماره_بند', '') if isinstance(x, dict) else ''
            )
            df['شماره_صفحه'] = df['ارجاع'].apply(
                lambda x: x.get('شماره_صفحه', '') if isinstance(x, dict) else ''
            )
            df = df.drop('ارجاع', axis=1)
        return df
    
    def flatten_array_fields(df):
        for col in df.columns:
            df[col] = df[col].apply(
                lambda x: ", ".join(x) if isinstance(x, list) else x
            )
        return df

    # ==================== MAIN APPLICATION ====================

    def main():
        # Initialize session state
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = None
        if 'results' not in st.session_state:
            st.session_state.results = None
        if 'current_tab' not in st.session_state:
            st.session_state.current_tab = 0
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📊 سیستم تحلیل هوشمند صورت‌های مالی</h1>
            <p class="main-subtitle">تحلیل حرفه‌ای گزارش‌های حسابرسی با هوش مصنوعی</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📁 بارگذاری فایل", "⚙️ پردازش و تحلیل", "📊 نتایج و گزارشات"])
        
        # ==================== TAB 1: FILE UPLOAD ====================
        with tab1:
            st.markdown("""
            <div class="alert-box alert-info">
                <div class="alert-title">📌 راهنمای بارگذاری فایل</div>
                <div class="alert-content">
                    <p><strong>فرمت‌های پشتیبانی شده:</strong></p>
                    <ul>
                        <li>✅ فایل‌های PDF با کیفیت بالا</li>
                        <li>✅ فایل‌های ZIP حاوی چندین PDF</li>
                        <li>✅ حداکثر حجم هر فایل: 50 مگابایت</li>
                    </ul>
                    <p><strong>استانداردهای مورد نیاز:</strong></p>
                    <ul>
                        <li>🔹 فایل‌ها باید شامل گزارش حسابرس مستقل باشند</li>
                        <li>🔹 صورت‌های مالی پیوست باید واضح و خوانا باشند</li>
                        <li>🔹 در صورت اسکن، رزولوشن حداقل 300 DPI توصیه می‌شود</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Upload method selection
            col1, col2 = st.columns(2)
            with col1:
                upload_method = st.radio(
                    "روش بارگذاری را انتخاب کنید:",
                    ["📄 فایل‌های جداگانه", "📦 فایل ZIP"],
                    horizontal=False
                )
            
            # File upload
            uploaded_files = None
            if upload_method == "📄 فایل‌های جداگانه":
                st.markdown("""
                <div class="upload-zone">
                    <div class="upload-icon">📁</div>
                    <div class="upload-title">فایل‌های PDF را بارگذاری کنید</div>
                    <div class="upload-subtitle">می‌توانید چندین فایل را همزمان انتخاب کنید</div>
                </div>
                """, unsafe_allow_html=True)
                
                uploaded_files = st.file_uploader(
                    "انتخاب فایل‌ها",
                    type=['pdf'],
                    accept_multiple_files=True,
                    label_visibility="collapsed"
                )
            else:
                st.markdown("""
                <div class="upload-zone">
                    <div class="upload-icon">📦</div>
                    <div class="upload-title">فایل ZIP را بارگذاری کنید</div>
                    <div class="upload-subtitle">فایل ZIP باید شامل فایل‌های PDF باشد</div>
                </div>
                """, unsafe_allow_html=True)
                
                zip_file = st.file_uploader(
                    "انتخاب فایل ZIP",
                    type=['zip'],
                    label_visibility="collapsed"
                )
                
                if zip_file:
                    try:
                        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                            pdf_files = []
                            for file_info in zip_ref.filelist:
                                if file_info.filename.lower().endswith('.pdf'):
                                    pdf_content = zip_ref.read(file_info.filename)
                                    pdf_files.append({
                                        'name': os.path.basename(file_info.filename),
                                        'content': pdf_content
                                    })
                        uploaded_files = pdf_files
                        st.markdown(f"""
                        <div class="alert-box alert-success">
                            <div class="alert-title">✅ استخراج موفق</div>
                            <div class="alert-content">{len(pdf_files)} فایل PDF از ZIP استخراج شد</div>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f"""
                        <div class="alert-box alert-danger">
                            <div class="alert-title">❌ خطا در استخراج</div>
                            <div class="alert-content">{str(e)}</div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Display uploaded files
            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                
                # File statistics
                st.markdown("""
                <h3 style="color: #2c3e50; margin: 2rem 0 1rem 0;">📊 آمار فایل‌های بارگذاری شده</h3>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                if isinstance(uploaded_files[0], dict):
                    total_size = sum(len(f['content']) for f in uploaded_files)
                else:
                    total_size = sum(f.size for f in uploaded_files)
                
                with col1:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #667eea; --gradient-end: #764ba2;">
                        <div class="metric-icon">📁</div>
                        <div class="metric-value">{len(uploaded_files)}</div>
                        <div class="metric-label">تعداد فایل</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #f093fb; --gradient-end: #f5576c;">
                        <div class="metric-icon">💾</div>
                        <div class="metric-value">{total_size / (1024*1024):.1f}</div>
                        <div class="metric-label">مگابایت</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #4facfe; --gradient-end: #00f2fe;">
                        <div class="metric-icon">✅</div>
                        <div class="metric-value">آماده</div>
                        <div class="metric-label">وضعیت</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # File list
                st.markdown("""
                <h3 style="color: #2c3e50; margin: 2rem 0 1rem 0;">📋 لیست فایل‌ها</h3>
                """, unsafe_allow_html=True)
                
                for i, file in enumerate(uploaded_files):
                    if isinstance(file, dict):
                        filename = file['name']
                        file_size = len(file['content']) / 1024
                    else:
                        filename = file.name
                        file_size = file.size / 1024
                    
                    st.markdown(f"""
                    <div class="file-card">
                        <div class="file-info">
                            <div class="file-icon">📄</div>
                            <div>
                                <div class="file-name">{i+1}. {filename}</div>
                                <div class="file-size">{file_size:.1f} کیلوبایت</div>
                            </div>
                        </div>
                        <div class="file-status status-ready">✓ آماده</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Navigation helper
                st.markdown("""
                <div class="nav-helper">
                    <div class="nav-helper-title">🎯 مرحله بعدی</div>
                    <div class="nav-helper-text">برای شروع تحلیل، به تب "پردازش و تحلیل" بروید ⬅️</div>
                </div>
                """, unsafe_allow_html=True)
            
            else:
                st.markdown("""
                <div class="alert-box alert-warning">
                    <div class="alert-title">⚠️ هنوز فایلی بارگذاری نشده</div>
                    <div class="alert-content">لطفاً فایل‌های PDF خود را بارگذاری کنید تا بتوانید به مرحله بعد بروید</div>
                </div>
                """, unsafe_allow_html=True)
        
        # ==================== TAB 2: PROCESSING ====================
        with tab2:
            if not st.session_state.uploaded_files:
                st.markdown("""
                <div class="alert-box alert-warning">
                    <div class="alert-title">⚠️ فایلی برای پردازش وجود ندارد</div>
                    <div class="alert-content">
                        <p>لطفاً ابتدا به تب "بارگذاری فایل" بروید و فایل‌های خود را بارگذاری کنید</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-box alert-info">
                    <div class="alert-title">🤖 تحلیل هوشمند با AI</div>
                    <div class="alert-content">
                        <p>سیستم از مدل‌های پیشرفته هوش مصنوعی برای تحلیل گزارش‌های حسابرسی استفاده می‌کند:</p>
                        <ul>
                            <li>🔍 استخراج خودکار اطلاعات کلیدی</li>
                            <li>📊 ارزیابی سطح ریسک</li>
                            <li>📋 تحلیل بند به بند گزارش</li>
                            <li>⚠️ شناسایی تخلفات و مسائل قانونی</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Processing summary
                st.markdown("""
                <h3 style="color: #2c3e50; margin: 2rem 0 1rem 0;">📊 خلاصه پردازش</h3>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #667eea; --gradient-end: #764ba2;">
                        <div class="metric-icon">📁</div>
                        <div class="metric-value">{len(st.session_state.uploaded_files)}</div>
                        <div class="metric-label">فایل آماده</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    estimated_time = len(st.session_state.uploaded_files) * 30
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #f093fb; --gradient-end: #f5576c;">
                        <div class="metric-icon">⏱️</div>
                        <div class="metric-value">{estimated_time}</div>
                        <div class="metric-label">ثانیه (تخمینی)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #4facfe; --gradient-end: #00f2fe;">
                        <div class="metric-icon">🤖</div>
                        <div class="metric-value">AI</div>
                        <div class="metric-label">تحلیل هوشمند</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Process button
                if st.button("🚀 شروع تحلیل", type="primary", key="start_analysis"):
                    analyzer = FinancialAnalyzer()
                    results = []
                    
                    st.markdown("""
                    <div class="alert-box alert-info">
                        <div class="alert-title">⏳ در حال پردازش...</div>
                        <div class="alert-content">لطفاً صبر کنید، این عملیات ممکن است چند دقیقه طول بکشد</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    total_files = len(st.session_state.uploaded_files)
                    
                    for i, file in enumerate(st.session_state.uploaded_files):
                        try:
                            if isinstance(file, dict):
                                filename = file['name']
                                file_content = file['content']
                            else:
                                filename = file.name
                                file_content = file.getvalue()
                            
                            status_text.markdown(f"""
                            <div class="alert-box alert-info">
                                <div class="alert-title">🔄 در حال تحلیل</div>
                                <div class="alert-content">فایل {i+1} از {total_files}: {filename}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            result = analyzer.extract_table_from_page(file_content)
                            results.append((filename, result))
                            
                            status_text.markdown(f"""
                            <div class="alert-box alert-success">
                                <div class="alert-title">✅ تحلیل موفق</div>
                                <div class="alert-content">{filename}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        except Exception as e:
                            error_result = {"error": f"خطا: {str(e)}"}
                            results.append((filename, error_result))
                            
                            status_text.markdown(f"""
                            <div class="alert-box alert-danger">
                                <div class="alert-title">❌ خطا در تحلیل</div>
                                <div class="alert-content">{filename}: {str(e)}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        progress_bar.progress((i + 1) / total_files)
                    
                    st.session_state.results = results
                    
                    status_text.markdown(f"""
                    <div class="alert-box alert-success">
                        <div class="alert-title">🎉 تحلیل تکمیل شد!</div>
                        <div class="alert-content">{len(results)} فایل پردازش شد</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="nav-helper">
                        <div class="nav-helper-title">🎯 مرحله بعدی</div>
                        <div class="nav-helper-text">برای مشاهده نتایج، به تب "نتایج و گزارشات" بروید ⬅️</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show previous results if exist
                if st.session_state.results:
                    st.markdown("""
                    <div class="alert-box alert-success">
                        <div class="alert-title">✅ نتایج قبلی موجود است</div>
                        <div class="alert-content">می‌توانید نتایج را در تب "نتایج و گزارشات" مشاهده کنید</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # ==================== TAB 3: RESULTS ====================
        with tab3:
            if not st.session_state.results:
                st.markdown("""
                <div class="alert-box alert-warning">
                    <div class="alert-title">⚠️ هنوز نتیجه‌ای وجود ندارد</div>
                    <div class="alert-content">
                        <p>لطفاً ابتدا فایل‌ها را بارگذاری کرده و تحلیل را انجام دهید</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                results = st.session_state.results
                
                # Results summary
                st.markdown("""
                <h3 style="color: #2c3e50; margin: 2rem 0 1rem 0;">📊 خلاصه نتایج</h3>
                """, unsafe_allow_html=True)
                
                successful = sum(1 for _, result in results if 'error' not in result)
                failed = len(results) - successful
                success_rate = (successful / len(results)) * 100 if results else 0
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #667eea; --gradient-end: #764ba2;">
                        <div class="metric-icon">📊</div>
                        <div class="metric-value">{len(results)}</div>
                        <div class="metric-label">کل فایل‌ها</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #4caf50; --gradient-end: #66bb6a;">
                        <div class="metric-icon">✅</div>
                        <div class="metric-value">{successful}</div>
                        <div class="metric-label">موفق</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #f44336; --gradient-end: #e57373;">
                        <div class="metric-icon">❌</div>
                        <div class="metric-value">{failed}</div>
                        <div class="metric-label">ناموفق</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="modern-metric" style="--gradient-start: #f093fb; --gradient-end: #f5576c;">
                        <div class="metric-icon">📈</div>
                        <div class="metric-value">{success_rate:.0f}%</div>
                        <div class="metric-label">نرخ موفقیت</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Results details
                st.markdown("""
                <h3 style="color: #2c3e50; margin: 2rem 0 1rem 0;">📋 جزئیات نتایج</h3>
                """, unsafe_allow_html=True)
                
                for filename, result in results:
                    if 'error' in result:
                        st.markdown(f"""
                        <div class="result-card" style="border-top-color: #f44336;">
                            <div class="result-header">
                                <div class="result-title">❌ {filename}</div>
                            </div>
                            <div class="alert-content" style="color: #f44336;">{result['error']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        try:
                            analysis = result['تحلیل_جامع_گزارش_حسابرسی']['بخش۱_خلاصه_و_اطلاعات_کلیدی']
                            company_name = analysis['نام_شرکت']
                            auditor_name = analysis['نام_حسابرس']
                            opinion_type = analysis['نوع_اظهارنظر']
                            risk_level = analysis['سطح_ریسک_کلی_بنا_به_نظر_مدل_زبانی']
                            financial_year = analysis['دوره_مالی']
                            
                            risk_classes = {
                                'پایین': 'risk-low',
                                'متوسط': 'risk-medium',
                                'بالا': 'risk-high',
                                'بحرانی': 'risk-critical'
                            }
                            risk_class = risk_classes.get(risk_level, 'risk-low')
                            
                            risk_icons = {
                                'پایین': '🟢',
                                'متوسط': '🟡',
                                'بالا': '🟠',
                                'بحرانی': '🔴'
                            }
                            risk_icon = risk_icons.get(risk_level, '⚪')
                            
                            risk_colors = {
                                'پایین': '#4caf50',
                                'متوسط': '#ff9800',
                                'بالا': '#ff5722',
                                'بحرانی': '#f44336'
                            }
                            border_color = risk_colors.get(risk_level, '#4caf50')
                            
                            st.markdown(f"""
                            <div class="result-card" style="border-top-color: {border_color};">
                                <div class="result-header">
                                    <div class="result-title">✅ {filename}</div>
                                    <div class="risk-badge {risk_class}">{risk_icon} {risk_level}</div>
                                </div>
                                <div class="info-grid">
                                    <div class="info-item">
                                        <div class="info-label">🏢 نام شرکت</div>
                                        <div class="info-value">{company_name}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">📅 دوره مالی</div>
                                        <div class="info-value">{financial_year}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">👨‍💼 حسابرس</div>
                                        <div class="info-value">{auditor_name}</div>
                                    </div>
                                    <div class="info-item">
                                        <div class="info-label">📋 نوع اظهارنظر</div>
                                        <div class="info-value">{opinion_type}</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        except:
                            st.markdown(f"""
                            <div class="result-card" style="border-top-color: #4caf50;">
                                <div class="result-header">
                                    <div class="result-title">✅ {filename}</div>
                                </div>
                                <div class="alert-content">تحلیل موفق - اطلاعات جزئی در دسترس نیست</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Download Excel
                st.markdown("""
                <h3 style="color: #2c3e50; margin: 3rem 0 1rem 0;">📥 دانلود گزارشات</h3>
                """, unsafe_allow_html=True)
                
                if st.button("📊 تبدیل به Excel و دانلود", type="primary"):
                    st.markdown("""
                    <div class="alert-box alert-info">
                        <div class="alert-title">⏳ در حال ایجاد فایل‌های Excel...</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <div class="alert-box alert-success">
                        <div class="alert-title">✅ فایل‌های Excel آماده دانلود هستند</div>
                    </div>
                    """, unsafe_allow_html=True)

    if __name__ == "__main__":
        main()
