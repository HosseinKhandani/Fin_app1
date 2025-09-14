import streamlit as st
import pathlib
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

# Enhanced CSS with RTL support and centered metrics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @font-face {
        font-family: 'B Mitra';
        src: url('data:font/woff2;base64,') format('woff2');
        font-display: swap;
    }
    
    * {
        font-family: 'B Mitra', 'Tahoma', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
        direction: rtl;
    }
    
    .stApp {
        background: transparent;
        direction: rtl;
    }
    
    /* Fix Streamlit RTL issues */
    .stSidebar {
        direction: rtl !important;
    }
    
    .stSidebar > div {
        direction: rtl !important;
    }
    
    .stExpander {
        direction: rtl !important;
    }
    
    .stExpander > div {
        direction: rtl !important;
    }
    
    .stExpander summary {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stExpander summary svg {
        margin-left: 0.5rem !important;
        margin-right: 0 !important;
    }
    
    /* Fix keyboard_double_array bug */
    .stExpander details summary::before {
        content: "" !important;
    }
    
    .stExpander details summary {
        list-style: none !important;
    }
    
    .stExpander details summary::-webkit-details-marker {
        display: none !important;
    }
    
    .stSelectbox label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stRadio label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stRadio > div {
        direction: rtl !important;
        flex-direction: row-reverse !important;
        gap: 2rem;
    }
    
    .stFileUploader label {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* Header Styles */
    .main-header {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        text-align: center;
        border-right: 5px solid #4A90E2;
        direction: rtl;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2C3E50;
        margin: 0;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: #7F8C8D;
        margin: 0;
        text-align: center;
    }
    
    /* Card Styles */
    .content-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
        border: 1px solid #E8E8E8;
        direction: rtl;
    }
    
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2C3E50;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        text-align: right;
        direction: rtl;
    }
    
    /* User-friendly Upload Area - Reduced height and no border */
    .upload-area {
        background: #F8FBFF;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        margin: 1rem 0;
        border: none;
        min-height: auto;
    }
    
    .upload-area:hover {
        background: #F0F8FF;
    }
    
    .upload-text {
        color: #4A90E2;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .upload-subtext {
        color: #7F8C8D;
        font-size: 0.9rem;
        text-align: center;
    }
    
    /* Centered Metrics */
    .metric-container {
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0;
        direction: rtl;
    }
    
    .metric-card {
        flex: 1;
        background: linear-gradient(135deg, #4A90E2, #357ABD);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center !important;
    }
    
    .metric-title {
        font-size: 0.9rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
        text-align: center !important;
        display: block;
        width: 100%;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        text-align: center !important;
        display: block;
        width: 100%;
    }
    
    /* Risk Level Background Colors */
    .risk-low {
        background: linear-gradient(135deg, #27AE60, #2ECC71) !important;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #F39C12, #E67E22) !important;
    }
    
    .risk-high {
        background: linear-gradient(135deg, #E67E22, #D35400) !important;
    }
    
    .risk-critical {
        background: linear-gradient(135deg, #E74C3C, #C0392B) !important;
    }
    
    /* Status Messages */
    .status-success {
        background: linear-gradient(135deg, #27AE60, #2ECC71);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: 500;
        direction: rtl;
        text-align: right;
    }
    
    .status-error {
        background: linear-gradient(135deg, #E74C3C, #C0392B);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: 500;
        direction: rtl;
        text-align: right;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #F39C12, #E67E22);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: 500;
        direction: rtl;
        text-align: right;
    }
    
    .status-info {
        background: linear-gradient(135deg, #3498DB, #2980B9);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: 500;
        direction: rtl;
        text-align: right;
    }
    
    /* Progress Bar */
    .progress-container {
        background: #F8F9FA;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #E9ECEF;
        direction: rtl;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4A90E2, #357ABD);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
        width: 100%;
        font-family: 'B Mitra', 'Tahoma', sans-serif !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #357ABD, #2E6DA4);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
    }
    
    /* Button spacing from cards */
    .stButton {
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Sidebar */
    .sidebar .stSelectbox > div > div {
        background: white;
        border: 1px solid #E8E8E8;
        border-radius: 8px;
        direction: rtl;
    }
    
    .api-status-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        border-right: 4px solid #4A90E2;
        direction: rtl;
    }
    
    .api-status-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid #F0F0F0;
        direction: rtl;
    }
    
    .api-status-item:last-child {
        border-bottom: none;
    }
    
    .api-status-label {
        color: #2C3E50;
        font-weight: 500;
    }
    
    .api-status-value {
        color: #4A90E2;
        font-weight: 600;
    }
    
    /* File List */
    .file-item {
        background: #F8F9FA;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-right: 3px solid #4A90E2;
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
    }
    
    .file-name {
        font-weight: 500;
        color: #2C3E50;
    }
    
    .file-size {
        color: #7F8C8D;
        font-size: 0.9rem;
    }
    
    /* Results */
    .result-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #E8E8E8;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        direction: rtl;
    }
    
    .company-info {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-top: 1rem;
        direction: rtl;
    }
    
    .info-item {
        background: #F8F9FA;
        padding: 0.75rem;
        border-radius: 6px;
        border-right: 3px solid #4A90E2;
        direction: rtl;
        text-align: center;
    }
    
    .info-label {
        font-size: 0.8rem;
        color: #7F8C8D;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-align: center !important;
    }
    
    .info-value {
        font-size: 1rem;
        color: #2C3E50;
        font-weight: 600;
        margin-top: 0.25rem;
        text-align: center !important;
    }
    
    /* Remove hover tooltips */
    .stButton > button[title] {
        title: none !important;
    }
    
    [title] {
        title: none !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Fix for file uploader */
    .stFileUploader > div {
        direction: rtl !important;
    }
    
    .stFileUploader button {
        font-family: 'B Mitra', 'Tahoma', sans-serif !important;
    }
    
    /* Remove file uploader border and dashes */
    .stFileUploader > div > div {
        border: none !important;
        background: #F8FBFF !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        min-height: auto !important;
    }
    
    .stFileUploader > div > div > div {
        border: none !important;
        border-style: none !important;
    }
    
    /* Fix columns RTL */
    .stColumn {
        direction: rtl !important;
    }
    
    /* Fix Streamlit metrics to center */
    .stMetric {
        text-align: center !important;
    }
    
    .stMetric > div {
        text-align: center !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .stMetric [data-testid="metric-container"] {
        text-align: center !important;
        justify-content: center !important;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    .stMetric [data-testid="metric-container"] > div {
        text-align: center !important;
        width: 100%;
    }
    
    /* Force center alignment for metric labels and values */
    .stMetric label {
        text-align: center !important;
        justify-content: center !important;
        display: flex;
        width: 100%;
    }
    
    .stMetric [data-testid="metric-value"] {
        text-align: center !important;
        justify-content: center !important;
        display: flex;
    }
</style>
""", unsafe_allow_html=True)

proxy_url = "http://185.173.168.31:22525"
os.environ['HTTP_PROXY'] = proxy_url
os.environ['HTTPS_PROXY'] = proxy_url

api_keys = [
    "AIzaSyAbWehhzebrPM3wLSh7DHNbrZ9JVOTfHWw",
    "AIzaSyBHBGLi-Uq-X4aEQiz7Epwy8sjnj3jY7Yo",
    "AIzaSyBeLYGH4JS-fPHYdqKgUPotV2dpGZYZ2to"
]

api_key_cycler = cycle(api_keys)

def get_client():
    """Return a new client configured with the next API key in a round-robin fashion."""
    api_key = next(api_key_cycler)
    return genai.Client(api_key=api_key)

class FinancialAnalyzer:
    def __init__(self):
        self.response_schema = {
            "type": "object",
            "properties": {
                "تحلیل_جامع_گزارش_حسابرسی": {
                    "type": "object",
                    "description": "ساختار اصلی که تحلیل کامل گزارش حسابرس را در خود جای می‌دهد.",
                    "properties": {
                        "بخش۱_خلاصه_و_اطلاعات_کلیدی": {
                            "type": "object",
                            "description": "شامل اطلاعات اولیه گزارش و نتیجه‌گیری‌های اصلی در یک نگاه.",
                            "properties": {
                                "نام_شرکت": {
                                    "type": "string",
                                    "description": "نام کامل شرکت از روی جلد گزارش."
                                },
                                "نام_حسابرس": {
                                    "type": "string",
                                    "description": "نام موسسه حسابرسی."
                                },
                                "دوره_مالی": {
                                    "type": "string",
                                    "description": "دوره مالی مورد رسیدگی، مثلا: 'سال مالی منتهی به ۲۹ اسفند ۱۳۹۸'."
                                },
                                "نوع_اظهارنظر": {
                                    "type": "string",
                                    "description": "یکی از موارد: مقبول، مشروط، مردود، عدم اظهارنظر.",
                                    "enum": ["مقبول", "مشروط", "مردود", "عدم اظهارنظر"]
                                },
                                "سطح_ریسک_کلی_بنا_به_نظر_بازرس": {
                                    "type": "string",
                                    "description": "سطح ریسک کلی استنباط شده از گزارش با توجه به نظر حسابرس و بازرس",
                                    "enum": ["پایین", "متوسط", "بالا", "بحرانی"]
                                },
                                "سطح_ریسک_کلی_بنا_به_نظر_مدل_زبانی": {
                                    "type": "string",
                                    "description": " سطح ریسک کلی استنباط شده از گزارش بنابه نظر مدل زبانی.",
                                    "enum": ["پایین", "متوسط", "بالا", "بحرانی"]
                                },
                                "جزییات_سطح_ریسک_تعیین_شده_توسط_مدل": {
                                    "type": "string",
                                    "description": " جزییات و دلیل سطح ریسک کلی استنباط شده از گزارش بنابه نظر مدل زبانی."
                                },
                                "نکات_کلیدی_و_نتیجه_گیری": {
                                    "type": "array",
                                    "description": "آرایه‌ای از ۳ رشته شامل مهم‌ترین یافته‌ها و نتیجه‌گیری‌ها.",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": [
                                "نام_شرکت", "نام_حسابرس", "دوره_مالی", "نوع_اظهارنظر",
                                "سطح_ریسک_کلی_بنا_به_نظر_بازرس", "سطح_ریسک_کلی_بنا_به_نظر_مدل_زبانی",
                                "جزییات_سطح_ریسک_تعیین_شده_توسط_مدل", "نکات_کلیدی_و_نتیجه_گیری"
                            ]
                        },
                        "بخش۲_تجزیه_تحلیل_گزارش": {
                            "type": "object",
                            "description": "تجزیه و تحلیل ساختاریافته متن گزارش، بند به بند.",
                            "properties": {
                                "بند_اظهارنظر": {
                                    "type": "object",
                                    "properties": {
                                        "نوع": {"type": "string"},
                                        "خلاصه_دلایل": {"type": "string"}
                                    },
                                    "required": ["نوع", "خلاصه_دلایل"]
                                },
                                "بند_مبانی_اظهارنظر": {
                                    "type": "object",
                                    "properties": {
                                        "موضوعیت_دارد": {"type": "boolean"},
                                        "موارد_مطرح_شده": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "شماره_مورد": {"type": "integer"},
                                                    "عنوان": {"type": "string"},
                                                    "شرح": {"type": "string"},
                                                    "نوع_دلیل": {
                                                        "type": "string",
                                                        "enum": ["محدودیت در رسیدگی", "انحراف از استانداردهای حسابداری", "سایر"]
                                                    }
                                                },
                                                "required": ["شماره_مورد", "عنوان", "شرح", "نوع_دلیل"]
                                            }
                                        }
                                    },
                                    "required": ["موضوعیت_دارد"]
                                },
                                "بند_تاکید_بر_مطالب_خاص": {
                                    "type": "object",
                                    "properties": {
                                        "موضوعیت_دارد": {"type": "boolean"},
                                        "موارد_مطرح_شده": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "عنوان": {"type": "string"},
                                                    "شرح": {"type": "string"},
                                                    "ریسک_برجسته_شده": {"type": "string"}
                                                },
                                                "required": ["عنوان", "شرح", "ریسک_برجسته_شده"]
                                            }
                                        }
                                    },
                                    "required": ["موضوعیت_دارد"]
                                },
                                "گزارش_رعایت_الزامات_قانونی": {
                                    "type": "object",
                                    "properties": {
                                        "موضوعیت_دارد": {"type": "boolean"},
                                        "تخلفات": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "عنوان_تخلف": {"type": "string"},
                                                    "شرح": {"type": "string"},
                                                    "مبانی_قانونی_و_استانداردها": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "string",
                                                            "enum": [
                                                                "قانون پولی و بانکی کشور",
                                                                "قانون عملیات بانکی بدون رباً",
                                                                "آیین نامه ها و دستورالعملهای بانک مرکزی (مهمترین بخش)",
                                                                "اساسنامه بانک",
                                                                "قانون تجارت (در موارد مرتبط)",
                                                                "استانداردهای حسابداری",
                                                                "استانداردهای حسابرسی"
                                                            ]
                                                        }
                                                    }
                                                },
                                                "required": ["عنوان_تخلف", "شرح", "مبانی_قانونی_و_استانداردها"]
                                            }
                                        }
                                    },
                                    "required": ["موضوعیت_دارد"]
                                }
                            }
                        },
                        "بخش۳_چک_لیست_موضوعی": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "موضوع": {
                                        "type": "string",
                                        "enum": [
                                            "کفایت سرمایه", "تسعیر ارز و عملیات خارجی", "مالیات و جرائم مالیاتی",
                                            "تجدید ارزیابی دارایی‌های ثابت و نامشهود", "تعهدات ارزی و اختلاف با بانک مرکزی",
                                            "تهاتر(Barter)", "عدم دریافت تأییدیه‌های حسابداری", "مغایرت‌های حساب جاری بانک مرکزی",
                                            "نسبت کفایت سرمایه", "نسبت ها در چارچوب بازل(bazel Accords)",
                                            "(Facilities and Credits)تسهیلات و اعتبارات", "سود سهام دولت",
                                            "پروژه‌های اجرایی ناتمام", "معاملات با اشخاص وابسته", "ذخیره گیری"
                                        ]
                                    },
                                    "در_گزارش_آمده": {"type": "boolean"},
                                    "وضعیت": {
                                        "type": "string",
                                        "enum": [
                                            "مصداق ندارد", "بررسی شده - ریسک خاصی گزارش نشده",
                                            "مسئله کلیدی منجر به اظهارنظر مشروط", "ریسک بحرانی"
                                        ]
                                    },
                                    "مقدار_عددی": {"type": "string","description": " مقدار عددی  در صورت وجود در گزارش بازرس و یا حسابرس. در صورت عدم وجود به متن صورت حساب وارد نشو و NaN برگردان. "},
                                    "جزئیات": {"type": "string"}
                                },
                                "required": ["موضوع", "در_گزارش_آمده", "وضعیت", "مقدار_عددی", "جزئیات"]
                            }
                        }
                    }
                }
            },
            "required": ["تحلیل_جامع_گزارش_حسابرسی"]
        }
    
    def extract_table_from_page(self, file_content):
        """Extract analysis from PDF using Gemini API with rotation - Direct processing without temp files"""
        client = get_client()
        
        prompt = """
        لطفاً گزارش حسابرسی ارائه شده را تحلیل کنید و اطلاعات را طبق ساختار JSON مشخص شده استخراج کنید.
        تمام فیلدهای required را با دقت تکمیل کنید و از enum های تعریف شده استفاده کنید.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=[
                types.Part.from_bytes(data=file_content, mime_type="application/pdf"),
                prompt
            ],
            config={
                'system_instruction': """شما به عنوان یک تحلیلگر مالی و حسابرس خبره عمل می‌کنید. وظیفه شما تحلیل گزارش حسابرس مستقل و بازرس قانونی به همراه صورت‌های مالی پیوست آن است 
                    لطفاً تمام فیلدها را با دقت و بر اساس اطلاعات موجود در سند تکمیل کنید.""",
                "response_mime_type": "application/json",
                "response_schema": self.response_schema,
                "temperature": 0.5
            }
        )
        
        if not response or not response.text:
            raise ValueError("API response was empty or invalid.")
        
        data = json.loads(response.text)
        return data

def create_header():
    """Create clean RTL header"""
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">📊 تحلیلگر هوشمند مالی</h1>
        <p class="main-subtitle">تحلیل هوشمند گزارش‌های مالی با قدرت Gemini 2.5 Pro</p>
    </div>
    """, unsafe_allow_html=True)

def create_api_status_sidebar():
    """Create clean API status in sidebar"""
    with st.sidebar:
        st.markdown(f"""
        <div class="api-status-card">
            <h3 style="color: #2C3E50; margin-bottom: 1rem;">🔗 وضعیت API</h3>
            <div class="api-status-item">
                <span class="api-status-label">تعداد کلیدها:</span>
                <span class="api-status-value">{len(api_keys)}</span>
            </div>
            <div class="api-status-item">
                <span class="api-status-label">پروکسی:</span>
                <span class="api-status-value">غیرفعال</span>
            </div>
            <div class="api-status-item">
                <span class="api-status-label">مدل:</span>
                <span class="api-status-value">Gemini 2.5 Pro</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_file_upload_section():
    """Create user-friendly file upload section"""
    st.markdown("""
    <div class="content-card">
        <h2 class="section-title">📁 بارگذاری فایل‌ها</h2>
    """, unsafe_allow_html=True)
    
    upload_method = st.radio(
        "روش بارگذاری:",
        ["فایل‌های جداگانه", "پوشه ZIP"],
        horizontal=True,
        key="upload_method"
    )
    
    uploaded_files = []
    
    if upload_method == "فایل‌های جداگانه":
        st.markdown("""
        <div class="upload-area">
            <div class="upload-text">📄 فایل های PDF خود را اینجا بارگذاری کنید</div>
            <div class="upload-subtext">فرمت‌های پشتیبانی شده: PDF - حداکثر حجم: 50 مگابایت</div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "انتخاب فایل‌ها",
            type=['pdf'],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
    
    else:  # ZIP upload
        st.markdown("""
        <div class="upload-area">
            <div class="upload-text">📦 انتخاب فایل ZIP</div>
            <div class="upload-subtext">فایل ZIP باید شامل فایل‌های PDF باشد</div>
        </div>
        """, unsafe_allow_html=True)
        
        zip_file = st.file_uploader(
            "انتخاب فایل ZIP",
            type=['zip'],
            label_visibility="collapsed"
        )
        
        if zip_file:
            # Extract ZIP files - process directly without creating temp files
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
                
                if pdf_files:
                    st.markdown(f"""
                    <div class="status-success">
                        ✅ {len(pdf_files)} فایل PDF از ZIP استخراج شد
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.markdown(f"""
                <div class="status-error">
                    ❌ خطا در استخراج ZIP: {str(e)}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    return uploaded_files

def create_processing_section(uploaded_files):
    """Create clean processing section with centered metrics"""
    if not uploaded_files:
        return None
    
    st.markdown("""
    <div class="content-card">
        <h2 class="section-title">🚀 آماده پردازش</h2>
    """, unsafe_allow_html=True)
    
    # File statistics with centered metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">تعداد فایل‌ها</div>
            <div class="metric-value">{len(uploaded_files)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Calculate total size based on file type
        if uploaded_files and isinstance(uploaded_files[0], dict):  # ZIP extracted files
            total_size = sum(len(f['content']) for f in uploaded_files)
        else:  # Regular uploaded files
            total_size = sum(f.size for f in uploaded_files)
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">حجم کل</div>
            <div class="metric-value">{total_size / (1024*1024):.1f} MB</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">وضعیت</div>
            <div class="metric-value">آماده</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add spacing before the button
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    # File list with custom expander to avoid keyboard_double_array bug
    if st.button("📋 لیست فایل ها", key="toggle_files"):
        st.session_state.show_files = not st.session_state.get('show_files', False)
    
    if st.session_state.get('show_files', False):
        for i, file in enumerate(uploaded_files):
            if isinstance(file, dict):  # ZIP extracted
                filename = file['name']
                file_size = len(file['content']) / 1024
            else:  # Regular upload
                filename = file.name
                file_size = file.size / 1024
            
            st.markdown(f"""
            <div class="file-item">
                <span class="file-name">{i+1}. {filename}</span>
                <span class="file-size">{file_size:.1f} KB</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Process button
    if st.button("🚀 شروع تحلیل", type="primary", key="process_btn"):
        return process_files(uploaded_files)
    
    return None

def process_files(uploaded_files):
    """Process files directly without creating temporary files"""
    analyzer = FinancialAnalyzer()
    results = []
    
    # Create progress tracking
    st.markdown("""
    <div class="progress-container">
        <h3 style="color: #2C3E50; margin-bottom: 1rem;">در حال پردازش...</h3>
    </div>
    """, unsafe_allow_html=True)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_files = len(uploaded_files)
    
    for i, file in enumerate(uploaded_files):
        try:
            # Get filename and content
            if isinstance(file, dict):  # ZIP extracted
                filename = file['name']
                file_content = file['content']
            else:  # Regular upload
                filename = file.name
                file_content = file.getvalue()
            
            # Update status
            status_text.markdown(f"""
            <div class="status-info">
                🔄 در حال تحلیل فایل {i+1} از {total_files}: {filename}
            </div>
            """, unsafe_allow_html=True)
            
            # Analyze directly with file content
            result = analyzer.extract_table_from_page(file_content)
            results.append((filename, result))
            
            # Show success
            status_text.markdown(f"""
            <div class="status-success">
                ✅ {filename} - تحلیل موفق
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            error_result = {"error": f"خطا در تحلیل: {str(e)}"}
            results.append((filename, error_result))
            
            status_text.markdown(f"""
            <div class="status-error">
                ❌ {filename} - خطا: {str(e)}
            </div>
            """, unsafe_allow_html=True)
        
        # Update progress
        progress_bar.progress((i + 1) / total_files)
    
    # Final status
    status_text.markdown(f"""
    <div class="status-success">
        🎉 تحلیل تکمیل شد! {len(results)} فایل پردازش شد
    </div>
    """, unsafe_allow_html=True)
    
    return results

def get_risk_class(risk_level):
    """Get CSS class for risk level"""
    risk_classes = {
        'پایین': 'risk-low',
        'متوسط': 'risk-medium', 
        'بالا': 'risk-high',
        'بحرانی': 'risk-critical'
    }
    return risk_classes.get(risk_level, '')

def create_results_section(results):
    """Create clean results section with risk-colored cards and centered metrics"""
    if not results:
        return
    
    st.markdown("""
    <div class="content-card">
        <h2 class="section-title">📊 نتایج تحلیل</h2>
    """, unsafe_allow_html=True)
    
    # Results summary with centered metrics
    successful = sum(1 for _, result in results if 'error' not in result)
    failed = len(results) - successful
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card risk-low">
            <div class="metric-title">موفق</div>
            <div class="metric-value">{successful}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card risk-critical">
            <div class="metric-title">ناموفق</div>
            <div class="metric-value">{failed}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        success_rate = (successful / len(results)) * 100 if results else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">درصد موفقیت</div>
            <div class="metric-value">{success_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Add spacing before the button
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    # Results details with custom toggle to avoid keyboard_double_array bug
    if st.button("🔍 جزئیات نتایج", key="toggle_results"):
        st.session_state.show_results = not st.session_state.get('show_results', True)
    
    if st.session_state.get('show_results', True):
        for filename, result in results:
            if 'error' in result:
                st.markdown(f"""
                <div class="result-item" style="border-right: 4px solid #E74C3C;">
                    <h4 style="color: #E74C3C; margin: 0;">❌ {filename}</h4>
                    <p style="color: #7F8C8D; margin: 0.5rem 0 0 0;">{result['error']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Extract company info for display
                try:
                    analysis = result['تحلیل_جامع_گزارش_حسابرسی']['بخش۱_خلاصه_و_اطلاعات_کلیدی']
                    company_name = analysis['نام_شرکت']
                    auditor_name = analysis['نام_حسابرس']
                    opinion_type = analysis['نوع_اظهارنظر']
                    risk_level = analysis['سطح_ریسک_کلی_بنا_به_نظر_مدل_زبانی']
                    
                    # Risk color coding
                    risk_colors = {
                        'پایین': '#27AE60',
                        'متوسط': '#F39C12',
                        'بالا': '#E67E22',
                        'بحرانی': '#E74C3C'
                    }
                    risk_color = risk_colors.get(risk_level, '#4A90E2')
                    risk_class = get_risk_class(risk_level)
                    
                    st.markdown(f"""
                    <div class="result-item" style="border-right: 4px solid #27AE60;">
                        <h4 style="color: #2C3E50; margin: 0 0 1rem 0;">✅ {filename}</h4>
                        <div class="company-info">
                            <div class="info-item">
                                <div class="info-label">شرکت</div>
                                <div class="info-value">{company_name}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">حسابرس</div>
                                <div class="info-value">{auditor_name}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">اظهارنظر</div>
                                <div class="info-value">{opinion_type}</div>
                            </div>
                            <div class="info-item {risk_class}" style="color: white;">
                                <div class="info-label" style="color: rgba(255,255,255,0.9);">سطح ریسک</div>
                                <div class="info-value" style="color: white;">{risk_level}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f"""
                    <div class="result-item" style="border-right: 4px solid #27AE60;">
                        <h4 style="color: #2C3E50; margin: 0;">✅ {filename}</h4>
                        <p style="color: #7F8C8D; margin: 0.5rem 0 0 0;">تحلیل موفق - جزئیات در دسترس نیست</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Convert to Excel
    if st.button("📊 تبدیل به Excel", type="secondary", key="excel_btn"):
        excel_files = convert_to_excel(results)
        
        if excel_files:
            st.markdown(f"""
            <div class="status-success">
                🎉 {len(excel_files)} فایل Excel ایجاد شد!
            </div>
            """, unsafe_allow_html=True)
            
            # Download section
            st.markdown("### 📥 دانلود فایل‌ها")
            
            for excel_file in excel_files:
                with open(excel_file, 'rb') as f:
                    st.download_button(
                        label=f"⬇️ دانلود {os.path.basename(excel_file)}",
                        data=f.read(),
                        file_name=os.path.basename(excel_file),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_{os.path.basename(excel_file)}"
                    )
    
    st.markdown("</div>", unsafe_allow_html=True)

def convert_to_excel(results):
    """Convert results to Excel files"""
    temp_dir = tempfile.mkdtemp()
    excel_files = []
    
    for filename, data in results:
        try:
            if "error" in data:
                continue
            
            report = data["تحلیل_جامع_گزارش_حسابرسی"]
            
            # Get company name for filename
            try:
                company_name = report["بخش۱_خلاصه_و_اطلاعات_کلیدی"]["نام_شرکت"]
                company_name = re.sub(r'[\\/:"*?<>|]+', "", company_name).strip()
                if not company_name:
                    company_name = f"Company_{len(excel_files) + 1}"
            except:
                company_name = f"Company_{len(excel_files) + 1}"
            
            output_file = os.path.join(temp_dir, f"{company_name}.xlsx")
            
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                # Section 1
                try:
                    part1 = report["بخش۱_خلاصه_و_اطلاعات_کلیدی"]
                    df1_data = {}
                    for k, v in part1.items():
                        if isinstance(v, list):
                            df1_data[k] = [", ".join(str(item) for item in v)]
                        else:
                            df1_data[k] = [str(v)]
                    
                    df1 = pd.DataFrame(df1_data)
                    df1.to_excel(writer, sheet_name="بخش1_خلاصه", index=False)
                except Exception as e:
                    st.warning(f"خطا در پردازش بخش 1: {str(e)}")
                
                # Section 2
                try:
                    part2 = report["بخش۲_تجزیه_تحلیل_گزارش"]
                    
                    # Opinion section
                    if "بند_اظهارنظر" in part2:
                        df_opinion = pd.DataFrame([part2["بند_اظهارنظر"]])
                        df_opinion.to_excel(writer, sheet_name="بند_اظهارنظر", index=False)
                    
                    # Basis of opinion
                    if "بند_مبانی_اظهارنظر" in part2:
                        basis_data = part2["بند_مبانی_اظهارنظر"]
                        if basis_data.get("موضوعیت_دارد", False) and "موارد_مطرح_شده" in basis_data:
                            df_basis = pd.DataFrame(basis_data["موارد_مطرح_شده"])
                        else:
                            df_basis = pd.DataFrame([{"موضوعیت_دارد": False}])
                        df_basis.to_excel(writer, sheet_name="بند_مبانی_اظهارنظر", index=False)
                    
                    # Emphasis section
                    if "بند_تاکید_بر_مطالب_خاص" in part2:
                        emphasis_data = part2["بند_تاکید_بر_مطالب_خاص"]
                        if emphasis_data.get("موضوعیت_دارد", False) and "موارد_مطرح_شده" in emphasis_data:
                            df_emphasis = pd.DataFrame(emphasis_data["موارد_مطرح_شده"])
                        else:
                            df_emphasis = pd.DataFrame([{"موضوعیت_دارد": False}])
                        df_emphasis.to_excel(writer, sheet_name="بند_تاکید_بر_مطالب_خاص", index=False)
                    
                    # Legal compliance
                    if "گزارش_رعایت_الزامات_قانونی" in part2:
                        legal_data = part2["گزارش_رعایت_الزامات_قانونی"]
                        if legal_data.get("موضوعیت_دارد", False) and "تخلفات" in legal_data:
                            violations = legal_data["تخلفات"]
                            processed_violations = []
                            
                            for violation in violations:
                                processed_violation = violation.copy()
                                if "مبانی_قانونی_و_استانداردها" in processed_violation:
                                    processed_violation["مبانی_قانونی_و_استانداردها"] = ", ".join(
                                        processed_violation["مبانی_قانونی_و_استانداردها"]
                                    )
                                processed_violations.append(processed_violation)
                            
                            df_legal = pd.DataFrame(processed_violations)
                        else:
                            df_legal = pd.DataFrame([{"موضوعیت_دارد": False}])
                        df_legal.to_excel(writer, sheet_name="گزارش_قانونی", index=False)
                
                except Exception as e:
                    st.warning(f"خطا در پردازش بخش 2: {str(e)}")
                
                # Section 3
                try:
                    if "بخش۳_چک_لیست_موضوعی" in report:
                        part3 = report["بخش۳_چک_لیست_موضوعی"]
                        df3 = pd.DataFrame(part3)
                        df3.to_excel(writer, sheet_name="بخش3_چک_لیست", index=False)
                except Exception as e:
                    st.warning(f"خطا در پردازش بخش 3: {str(e)}")
            
            excel_files.append(output_file)
            
        except Exception as e:
            st.error(f"خطا در ایجاد Excel برای {filename}: {str(e)}")
    
    return excel_files

def create_info_panel():
    """Create information panel in sidebar"""
    with st.sidebar:
        st.markdown("""
        <div class="api-status-card">
            <h3 style="color: #2C3E50; margin-bottom: 1rem;">ℹ️ راهنمای استفاده</h3>
            <div style="color: #7F8C8D; line-height: 1.6;">
                <p>• فایل‌های PDF گزارش‌های حسابرسی خود را بارگذاری کنید</p>
                <p>• سیستم از چندین کلید API به صورت چرخشی استفاده می‌کند</p>
                <p>• نتایج بصورت اکسل قابل دانلود است</p>
                <p>• تحلیل شامل سه بخش اصلی است:</p>
                <ul style="margin-right: 1rem;">
                    <li>خلاصه و اطلاعات کلیدی</li>
                    <li>تجزیه و تحلیل گزارش</li>
                    <li>چک لیست موضوعی</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'show_files' not in st.session_state:
        st.session_state.show_files = False
    if 'show_results' not in st.session_state:
        st.session_state.show_results = True
    
    # Create header
    create_header()
    
    # Create sidebar panels
    create_api_status_sidebar()
    create_info_panel()
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # File upload section
        uploaded_files = create_file_upload_section()
        
        # Processing section
        if uploaded_files:
            results = create_processing_section(uploaded_files)
            if results:
                st.session_state.results = results
        
        # Results section
        if st.session_state.results:
            create_results_section(st.session_state.results)
    
    with col2:
        # Statistics panel with centered metrics
        if st.session_state.results:
            st.markdown("""
            <div class="content-card">
                <h3 style="color: #2C3E50; margin-bottom: 1rem; text-align: center;">📈 آمار کلی</h3>
            """, unsafe_allow_html=True)
            
            total_files = len(st.session_state.results)
            successful = sum(1 for _, result in st.session_state.results if 'error' not in result)
            success_rate = (successful / total_files) * 100 if total_files > 0 else 0
            
            # Use centered metric cards instead of st.metric
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 1rem;">
                <div class="metric-title">کل فایل‌ها</div>
                <div class="metric-value">{total_files}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 1rem;">
                <div class="metric-title">تحلیل موفق</div>
                <div class="metric-value">{successful}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 1rem;">
                <div class="metric-title">درصد موفقیت</div>
                <div class="metric-value">{success_rate:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()