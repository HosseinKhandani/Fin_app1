                                    "مبانی_قانونی_و_استانداردها": {
                                        "type": "array",
                                        "items": {
                                        "type": "string",
                                        "enum": ["قانون پولی و بانکی کشور", "قانون عملیات بانکی بدون رباً", "آیین نامه ها و دستورالعملهای بانک مرکزی (مهمترین بخش)", "اساسنامه بانک", "قانون تجارت (در موارد مرتبط)", "استانداردهای حسابداری", "استانداردهای حسابرسی"]
                                        }
                                    }
                                    },
                                    "required": ["ارجاع", "عنوان_تخلف", "شرح", "مبانی_قانونی_و_استانداردها"]
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
                            "موضوع": {"type": "string", "enum": ["کفایت سرمایه", "تسعیر ارز و عملیات خارجی", "مالیات و جرائم مالیاتی", "تجدید ارزیابی دارایی‌های ثابت و نامشهود", "تعهدات ارزی و اختلاف با بانک مرکزی", "تهاتر(Barter)", "عدم دریافت تأییدیه‌های حسابداری", "مغایرت‌های حساب جاری بانک مرکزی", "نسبت کفایت سرمایه", "نسبت ها در چارچوب بازل(bazel Accords)", "(Facilities and Credits)تسهیلات و اعتبارات", "سود سهام دولت", "پروژه‌های اجرایی ناتمام", "معاملات با اشخاص وابسته", "ذخیره گیری"]},
                            "در_گزارش_آمده": {"type": "boolean"},
                            "وضعیت": {"type": "string", "enum": ["مصداق ندارد", "بررسی شده - ریسک خاصی گزارش نشده", "مسئله کلیدی منجر به اظهارنظر مشروط", "ریسک بحرانی"]},
                            "جزئیات": {"type": "string"},
                            "ارجاع": {
                                "type": "object",
                                "description": "ارجاع به شماره بند و صفحه مربوطه در گزارش اصلی.",    
                                "properties": {
                                "شماره_بند": {"type": "string", "description": "شماره بند مربوطه در گزارش حسابرس مستقل و بازرس قانونی .بین بند ها , قرار بده مانند ۲,۶"},
                                "شماره_صفحه": {"type": "string", "description": "شماره صفحه مربوطه در گزارش حسابرس مستقل و بازرس قانونی.چنانچه این مورد در چند بند به ان اشاره شده صفحات منطبق با بند را به ترتیب بند برگردان بین صفحات , قرار بده مانند ۱,۵"}
                                }
                            }
                            },
                            "required": ["موضوع", "در_گزارش_آمده", "وضعیت", "جزئیات", "ارجاع"]
                        }
                        }
                    }
                    }
                },
                "required": ["تحلیل_جامع_گزارش_حسابرسی"]
                }
        
        def extract_table_from_page(self, file_content):
            client = get_client()
            prompt = """لطفاً گزارش حسابرس مستقل و بازرس قانونی ارائه شده را تحلیل کنید و اطلاعات را طبق ساختار JSON مشخص شده استخراج کنید. تمام فیلدهای required را با دقت تکمیل کنید و از enum های تعریف شده استفاده کنید."""
            
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[types.Part.from_bytes(data=file_content, mime_type="application/pdf"), prompt],
                config={'system_instruction': """شما به عنوان یک تحلیلگر مالی و حسابرس خبره عمل می‌کنید. وظیفه شما تحلیل گزارش حسابرس مستقل و بازرس قانونی آن است . دقت کن که در تحلیل ها و ارجاعات به صفحات و بندها از گزارش حسابرس مستقل و بازرس قانونی استفاده کن و به متن صورتمالی مراجعه نکن , لطفاً تمام فیلدها را با دقت و بر اساس اطلاعات موجود در سند تکمیل کنید""", "response_mime_type": "application/json", "response_schema": self.response_schema, "temperature": 0.5}
            )
            
            return json.loads(response.text)

    # Main App
    def main():
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = None
        if 'results' not in st.session_state:
            st.session_state.results = None
        
        st.markdown("""
        <div class="main-header">
            <h1 class="main-title">📊 سیستم تحلیل هوشمند صورت‌های مالی</h1>
            <p class="main-subtitle">تحلیل حرفه‌ای گزارش‌های حسابرسی با هوش مصنوعی</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📁 بارگذاری فایل", "⚙️ پردازش و نتایج"])
        
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
                    <p style="margin-top: 1rem;"><strong>💡 نکات مهم:</strong></p>
                    <ul>
                        <li>📄 فایل‌ها باید گزارش حسابرس مستقل و بازرس قانونی باشند</li>
                        <li>🎯 کیفیت اسکن فایل‌ها بر دقت تحلیل تأثیرگذار است</li>
                        <li>⚡ پردازش هر فایل حدود 30 ثانیه زمان می‌برد</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                upload_method = st.radio("روش بارگذاری را انتخاب کنید:", ["📄 فایل‌های جداگانه", "📦 فایل ZIP"], horizontal=False)
            
            uploaded_files = None
            if upload_method == "📄 فایل‌های جداگانه":
                uploaded_files = st.file_uploader("انتخاب فایل‌ها", type=['pdf'], accept_multiple_files=True, label_visibility="collapsed")
            else:
                st.markdown("""
                <div style="background: #F8FBFF; border-radius: 12px; padding: 2rem; text-align: center; margin: 1rem 0;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📦</div>
                    <div style="font-size: 1.2rem; font-weight: 600; color: #667eea;">فایل ZIP را بارگذاری کنید</div>
                    <div style="color: #6c757d; margin-top: 0.5rem;">فایل ZIP باید شامل فایل‌های PDF باشد</div>
                </div>
                """, unsafe_allow_html=True)
                
                zip_file = st.file_uploader("انتخاب فایل ZIP", type=['zip'], label_visibility="collapsed")
                
                if zip_file:
                    try:
                        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                            pdf_files = []
                            for file_info in zip_ref.filelist:
                                if file_info.filename.lower().endswith('.pdf'):
                                    pdf_content = zip_ref.read(file_info.filename)
                                    pdf_files.append({'name': os.path.basename(file_info.filename), 'content': pdf_content})
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
            
            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                
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
                
                st.markdown("""
                <div class="nav-helper">
                    <div class="nav-helper-title">🎯 مرحله بعدی</div>
                    <div class="nav-helper-text">برای شروع تحلیل و مشاهده نتایج، به تب "پردازش و نتایج" بروید ⬅️</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-box alert-warning">
                    <div class="alert-title">⚠️ هنوز فایلی بارگذاری نشده</div>
                    <div class="alert-content">لطفاً فایل‌های PDF خود را بارگذاری کنید</div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            if not st.session_state.uploaded_files:
                st.markdown("""
                <div class="alert-box alert-warning">
                    <div class="alert-title">⚠️ فایلی برای پردازش وجود ندارد</div>
                    <div class="alert-content">
                        <p>لطفاً ابتدا به تب "بارگذاری فایل" بروید و فایل‌های PDF خود را بارگذاری کنید.</p>
                        <p style="margin-top: 1rem;"><strong>مراحل لازم:</strong></p>
                        <ol>
                            <li>به تب "بارگذاری فایل" بروید</li>
                            <li>فایل‌های PDF یا ZIP خود را انتخاب کنید</li>
                            <li>پس از بارگذاری موفق، به این تب برگردید</li>
                        </ol>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-box alert-info">
                    <div class="alert-title">🤖 تحلیل هوشمند با AI</div>
                    <div class="alert-content">
                        <p><strong>قابلیت‌های سیستم:</strong></p>
                        <ul>
                            <li>🔍 <strong>استخراج خودکار:</strong> اطلاعات کلیدی از گزارش حسابرسی</li>
                            <li>📊 <strong>ارزیابی ریسک:</strong> تعیین سطح ریسک بر اساس معیارهای حسابرسی</li>
                            <li>📋 <strong>تحلیل جامع:</strong> بررسی بند به بند گزارش</li>
                            <li>📥 <strong>خروجی اکسل:</strong> دانلود نتایج به صورت فایل اکسل ساختاریافته</li>
                        </ul>
                    </div>
                </div>
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
                        <div class="metric-label">ثانیه (تخمین)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown("""
                    <div class="modern-metric" style="--gradient-start: #4facfe; --gradient-end: #00f2fe;">
                        <div class="metric-icon">🤖</div>
                        <div class="metric-value">Gemini 2.5 Pro</div>
                        <div class="metric-label">مدل AI</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("🚀 شروع تحلیل", type="primary", key="start_analysis"):
                    analyzer = FinancialAnalyzer()
                    results = []
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    time_text = st.empty()
                    
                    total_files = len(st.session_state.uploaded_files)
                    estimated_time_per_file = 30
                    
                    for i, file in enumerate(st.session_state.uploaded_files):
                        try:
                            if isinstance(file, dict):
                                filename = file['name']
                                file_content = file['content']
                            else:
                                filename = file.name
                                file_content = file.getvalue()
                            
                            remaining_files = total_files - i
                            remaining_time = remaining_files * estimated_time_per_file
                            
                            status_text.markdown(f"""
                            <div class="alert-box alert-info">
                                <div class="alert-title">⏳ در حال پردازش...</div>
                                <div class="alert-content">
                                    <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">📄 فایل {i+1} از {total_files}: <strong>{filename}</strong></p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            time_text.markdown(f"""
                            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        padding: 1.5rem; border-radius: 15px; text-align: center; 
                                        color: white; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                                        margin-bottom: 1rem;">
                                <div style="font-size: 3rem; margin-bottom: 0.5rem;">⏳</div>
                                <div style="font-size: 1.8rem; font-weight: 700; margin-bottom: 0.3rem;">
                                    {remaining_time} ثانیه
                                </div>
                                <div style="font-size: 1rem; opacity: 0.9;">
                                    زمان تقریبی باقیمانده
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            result = analyzer.extract_table_from_page(file_content)
                            results.append((filename, result))
                            
                        except Exception as e:
                            error_result = {"error": f"خطا: {str(e)}"}
                            results.append((filename, error_result))
                        
                        progress_bar.progress((i + 1) / total_files)
                    
                    st.session_state.results = results
                    
                    time_text.empty()
                    status_text.markdown(f"""
                    <div class="alert-box alert-success">
                        <div class="alert-title">🎉 تحلیل تکمیل شد!</div>
                        <div class="alert-content">{len(results)} فایل با موفقیت پردازش شد</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.session_state.results:
                    st.markdown("""
                    <hr style="margin: 3rem 0; border: none; height: 2px; background: linear-gradient(90deg, transparent, #667eea, transparent);">
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <h3 style="color: #2c3e50; margin: 2rem 0 1rem 0;">📋 جزئیات نتایج</h3>
                    """, unsafe_allow_html=True)
                    
                    results = st.session_state.results
                    
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
                    
                    st.markdown("""
                    <h3 style="color: #2c3e50; margin: 2rem 0 1rem 0;">📄 نمایش نتایج</h3>
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
                                risk_level = analysis['سطح_ریسک_کلی_بنا_به_گزارش']
                                financial_year = analysis['دوره_مالی']
                                
                                risk_colors = {'پایین': '#4caf50', 'متوسط': '#ff9800', 'بالا': '#f44336', 'بحرانی': '#f44336'}
                                border_color = risk_colors.get(risk_level, '#4caf50')
                                
                                risk_card_classes = {'پایین': 'risk-card-low', 'متوسط': 'risk-card-medium', 'بالا': 'risk-card-high', 'بحرانی': 'risk-card-critical'}
                                risk_card_class = risk_card_classes.get(risk_level, 'risk-card-low')
                                
                                risk_icons = {'پایین': '🟢', 'متوسط': '🟡', 'بالا': '🟠', 'بحرانی': '🔴'}
                                risk_icon = risk_icons.get(risk_level, '⚪')
                                
                                st.markdown(f"""
                                <div class="result-card" style="border-top-color: {border_color};">
                                    <div class="result-header">
                                        <div class="result-title">✅ {filename}</div>
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
                                    </div>
                                    <div class="info-grid" style="margin-top: 1rem;">
                                        <div class="info-item">
                                            <div class="info-label">📋 نوع اظهارنظر</div>
                                            <div class="info-value">{opinion_type}</div>
                                        </div>
                                        <div class="risk-card {risk_card_class}">
                                            <div class="info-label">🎯 سطح ریسک</div>
                                            <div class="info-value" style="font-size: 1.5rem;">{risk_icon} {risk_level}</div>
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
                                    <div class="alert-content">تحلیل موفق</div>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Download Excel Section
                    st.markdown("""
                    <hr style="margin: 3rem 0; border: none; height: 2px; background: linear-gradient(90deg, transparent, #667eea, transparent);">
                    """, unsafe_allow_html=True)
                    
                    st.markdown("""
                    <h3 style="color: #2c3e50; margin: 2rem 0 1rem 0;">📥 دانلود نتایج</h3>
                    <div class="alert-box alert-info">
                        <div class="alert-title">📊 خروجی فایل اکسل</div>
                        <div class="alert-content">
                            <p><strong>فایل اکسل شامل اطلاعات زیر است:</strong></p>
                            <ul>
                                <li>📋 <strong>بخش 1:</strong> خلاصه و اطلاعات کلیدی (نام شرکت، حسابرس، سطح ریسک)</li>
                                <li>📄 <strong>بخش 2:</strong> تجزیه تحلیل گزارش (اظهارنظر، مبانی، تاکید، الزامات قانونی)</li>
                                <li>✅ <strong>بخش 3:</strong> چک لیست موضوعی با ارجاعات کامل</li>
                            </ul>
                            <p style="margin-top: 1rem;">🔍 هر گزارش در شیت‌های جداگانه با نام شرکت و سال مالی</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    def flatten_reference_data(df):
                        if 'ارجاع' in df.columns:
                            df['شماره_بند'] = df['ارجاع'].apply(lambda x: x.get('شماره_بند', '') if isinstance(x, dict) else '')
                            df['شماره_صفحه'] = df['ارجاع'].apply(lambda x: x.get('شماره_صفحه', '') if isinstance(x, dict) else '')
                            df = df.drop('ارجاع', axis=1)
                        return df
                    
                    def flatten_array_fields(df):
                        for col in df.columns:
                            df[col] = df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
                        return df
                    
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        for filename, result in results:
                            if 'error' in result:
                                continue
                            
                            try:
                                report = result["تحلیل_جامع_گزارش_حسابرسی"]
                                company_name = report["بخش۱_خلاصه_و_اطلاعات_کلیدی"]["نام_شرکت"]
                                financial_year = report["بخش۱_خلاصه_و_اطلاعات_کلیدی"]["دوره_مالی"]
                                
                                year_match = re.search(r'(\d{4})', financial_year)
                                year = year_match.group(1) if year_match else "Unknown"
                                
                                clean_company = re.sub(r'[\\/:"*?<>|]+', "", company_name).strip()[:20]
                                sheet_prefix = f"{clean_company}_{year}"
                                
                                # Section 1
                                part1 = report["بخش۱_خلاصه_و_اطلاعات_کلیدی"]
                                df1 = pd.DataFrame.from_dict({k: [v] if not isinstance(v, list) else [", ".join(v)] for k, v in part1.items()})
                                sheet_name1 = f"{sheet_prefix}_خلاصه"[:31]
                                df1.to_excel(writer, sheet_name=sheet_name1, index=False)
                                
                                # Section 2
                                if "بخش۲_تجزیه_تحلیل_گزارش" in report:
                                    part2 = report["بخش۲_تجزیه_تحلیل_گزارش"]
                                    
                                    if "بند_اظهارنظر" in part2:
                                        df_opinion = pd.DataFrame([part2["بند_اظهارنظر"]])
                                        sheet_name = f"{sheet_prefix}_اظهارنظر"[:31]
                                        df_opinion.to_excel(writer, sheet_name=sheet_name, index=False)
                                    
                                    if "بند_مبانی_اظهارنظر" in part2:
                                        basis_data = part2["بند_مبانی_اظهارنظر"]
                                        if basis_data.get("موضوعیت_دارد", False) and "موارد_مطرح_شده" in basis_data:
                                            df_basis = pd.DataFrame(basis_data["موارد_مطرح_شده"])
                                            df_basis = flatten_reference_data(df_basis)
                                            df_basis = flatten_array_fields(df_basis)
                                        else:
                                            df_basis = pd.DataFrame([{"موضوعیت_دارد": False}])
                                        sheet_name = f"{sheet_prefix}_مبانی"[:31]
                                        df_basis.to_excel(writer, sheet_name=sheet_name, index=False)
                                    
                                    if "بند_تاکید_بر_مطالب_خاص" in part2:
                                        emphasis_data = part2["بند_تاکید_بر_مطالب_خاص"]
                                        if emphasis_data.get("موضوعیت_دارد", False) and "موارد_مطرح_شده" in emphasis_data:
                                            df_emphasis = pd.DataFrame(emphasis_data["موارد_مطرح_شده"])
                                            df_emphasis = flatten_reference_data(df_emphasis)
                                            df_emphasis = flatten_array_fields(df_emphasis)
                                        else:
                                            df_emphasis = pd.DataFrame([{"موضوعیت_دارد": False}])
                                        sheet_name = f"{sheet_prefix}_تاکید"[:31]
                                        df_emphasis.to_excel(writer, sheet_name=sheet_name, index=False)
                                    
                                    if "گزارش_رعایت_الزامات_قانونی" in part2:
                                        legal_data = part2["گزارش_رعایت_الزامات_قانونی"]
                                        if legal_data.get("موضوعیت_دارد", False) and "تخلفات" in legal_data:
                                            violations = legal_data["تخلفات"]
                                            processed_violations = []
                                            for violation in violations:
                                                processed_violation = violation.copy()
                                                if "مبانی_قانونی_و_استانداردها" in processed_violation:
                                                    processed_violation["مبانی_قانونی_و_استانداردها"] = ", ".join(processed_violation["مبانی_قانونی_و_استانداردها"])
                                                processed_violations.append(processed_violation)
                                            df_legal = pd.DataFrame(processed_violations)
                                            df_legal = flatten_reference_data(df_legal)
                                            df_legal = flatten_array_fields(df_legal)
                                        else:
                                            df_legal = pd.DataFrame([{"موضوعیت_دارد": False}])
                                        sheet_name = f"{sheet_prefix}_قانونی"[:31]
                                        df_legal.to_excel(writer, sheet_name=sheet_name, index=False)
                                
                                # Section 3
                                if "بخش۳_چک_لیست_موضوعی" in report:
                                    part3 = report["بخش۳_چک_لیست_موضوعی"]
                                    df3 = pd.DataFrame(part3)
                                    df3 = flatten_reference_data(df3)
                                    df3 = flatten_array_fields(df3)
                                    sheet_name = f"{sheet_prefix}_چک_لیست"[:31]
                                    df3.to_excel(writer, sheet_name=sheet_name, index=False)
                                
                                # Adjust columns
                                for sheet_name in writer.sheets:
                                    worksheet = writer.sheets[sheet_name]
                                    for column in worksheet.columns:
                                        max_length = 0
                                        column_letter = column[0].column_letter
                                        for cell in column:
                                            try:
                                                if len(str(cell.value)) > max_length:
                                                    max_length = len(str(cell.value))
                                            except:
                                                pass
                                        adjusted_width = min(max_length + 2, 60)
                                        worksheet.column_dimensions[column_letter].width = adjusted_width
                            
                            except Exception as e:
                                st.warning(f"خطا در پردازش {filename}: {str(e)}")
                                continue
                    
                    excel_file = output.getvalue()
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📥 دانلود فایل اکسل کامل",
                            data=excel_file,
                            file_name=f"تحلیل_کامل_مالی_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    successful_results = [r for r in results if 'error' not in r[1]]
                    st.markdown(f"""
                    <div class="alert-box alert-success">
                        <div class="alert-title">✅ آماده دانلود</div>
                        <div class="alert-content">
                            <p><strong>فایل اکسل شامل تحلیل کامل {len(successful_results)} گزارش:</strong></p>
                            <ul>
                                <li>📊 <strong>بخش 1:</strong> خلاصه و اطلاعات کلیدی</li>
                                <li>📋 <strong>بخش 2:</strong> تجزیه تحلیل گزارش (اظهارنظر، مبانی، تاکید، الزامات قانونی)</li>
                                <li>✅ <strong>بخش 3:</strong> چک لیست موضوعی</li>
                            </ul>
                            <p style="margin-top: 1rem;">✨ هر گزارش در شیت‌های جداگانه با نام شرکت و سال مالی</p>
                            <p>🔍 تمامی ارجاعات به بند و صفحه در ستون‌های جداگانه</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    if __name__ == "__main__":
        main()
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import json
import pandas as pd
from google import genai
from google.genai import types
import os
import tempfile
import zipfile
from itertools import cycle
import time
import re
from io import BytesIO
import bcrypt

# Page configuration
st.set_page_config(
    page_title="AI Financial Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

api_keys = [
    "AIzaSyAo5oFZqsTRkUIqJRjoefWINWpbwPHbEn8",
    "AIzaSyBeLYGH4JS-fPHYdqKgUPotV2dpGZYZ2to",
    "AIzaSyDyj1DlOLAlbKzTLFP2tz95TcIca4oV0Vg"
]

# ==================== AUTHENTICATION ====================

config_path = 'config.yaml'
if not os.path.exists(config_path):
    default_config = {
        'credentials': {
            'usernames': {
                'admin': {'email': 'admin@example.com', 'name': 'مدیر سیستم', 'password': 'placeholder'},
                'fin.analyst': {'email': 'analyst@example.com', 'name': 'تحلیلگر مالی', 'password': 'placeholder'},
                'h.khandani': {'email': 'khandani@example.com', 'name': 'مدیر', 'password': 'placeholder'}
            }
        },
        'cookie': {'name': 'financial_analyzer_cookie', 'key': 'random_signature_key_12345', 'expiry_days': 30}
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, allow_unicode=True)

with open('config.yaml', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

config['credentials']['usernames']['admin']['password'] = hash_password("elnagh")
config['credentials']['usernames']['fin.analyst']['password'] = hash_password("abc_fin_cba")
config['credentials']['usernames']['h.khandani']['password'] = hash_password("123")

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None

if st.session_state.authentication_status is None:
    try:
        authenticator.login()
        if st.session_state.get("authentication_status"):
            st.session_state.name = st.session_state.get("name")
            st.session_state.username = st.session_state.get("username")
    except:
        try:
            name, authentication_status, username = authenticator.login('main')
            st.session_state.authentication_status = authentication_status
            st.session_state.name = name
            st.session_state.username = username
        except:
            result = authenticator.login()
            if result:
                st.session_state.name = result[0]
                st.session_state.authentication_status = result[1]
                st.session_state.username = result[2]

if st.session_state.get('authentication_status') == False:
    st.error('نام کاربری یا رمز عبور اشتباه است')
    st.stop()

if st.session_state.get('authentication_status') is None:
    st.warning('لطفاً نام کاربری و رمز عبور خود را وارد کنید')
    st.stop()

# ==================== MAIN APP ====================
if st.session_state.get('authentication_status'):
    
    # Sidebar
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
    
    # CSS
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
        
        .alert-box {
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-right: 5px solid;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            animation: slideIn 0.5s ease;
        }
        
        @keyframes slideIn {
            from {opacity: 0; transform: translateY(-20px);}
            to {opacity: 1; transform: translateY(0);}
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
        
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
            border-radius: 10px;
        }
        
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
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
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
        
        .risk-card {
            background: white;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 3px solid;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .risk-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .risk-card-low {
            border-color: #4caf50;
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        }
        
        .risk-card-medium {
            border-color: #ff9800;
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        }
        
        .risk-card-high {
            border-color: #f44336;
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        }
        
        .risk-card-critical {
            border-color: #d32f2f;
            background: linear-gradient(135deg, #ffcdd2 0%, #ef5350 100%);
        }
        
        .risk-card .info-label {
            color: #2c3e50 !important;
        }
        
        .risk-card .info-value {
            color: #2c3e50 !important;
        }
        
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
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stFileUploader > div {
            direction: rtl !important;
        }
        
        .stSelectbox label, .stRadio label {
            direction: rtl !important;
            text-align: right !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # API Setup
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
                    "description": "ساختار اصلی که تحلیل کامل گزارش حسابرس مستقل و بازرس قانونی را در خود جای می‌دهد.",
                    "properties": {
                        "بخش۱_خلاصه_و_اطلاعات_کلیدی": {
                        "type": "object",
                        "description": "شامل اطلاعات اولیه گزارش و نتیجه‌گیری‌های اصلی در یک نگاه.",
                        "properties": {
                            "نام_شرکت": {"type": "string", "description": "نام کامل شرکت از روی جلد گزارش."},
                            "نام_حسابرس": {"type": "string", "description": "نام موسسه حسابرسی."},
                            "دوره_مالی": {"type": "string", "description": "دوره مالی مورد رسیدگی، مثلا: 'سال مالی منتهی به ۲۹ اسفند ۱۳۹۸'."},
                            "نوع_اظهارنظر": {"type": "string", "description": "یکی از موارد: مقبول، مشروط، مردود، عدم اظهارنظر.", "enum": ["مقبول", "مشروط", "مردود", "عدم اظهارنظر"]},
                            "سطح_ریسک_کلی_بنا_به_گزارش": {"type": "string", "description": "سطح ریسک کلی استنباط شده از گزارش حسابرس مستقل و بازرس قانونی بنا به متن گزارش و شواهد و آماره های بیان شده از دیدگاه حسابرسی", "enum": ["پایین", "متوسط", "بالا", "بحرانی"]},
                            "جزییات_سطح_ریسک_تعیین_شده": {"type": "string", "description": " جزییات و دلیل سطح ریسک کلی استنباط شده از گزارش ."},
                            "نکات_کلیدی_و_نتیجه_گیری": {"type": "array", "description": "آرایه‌ای از ۳ رشته شامل مهم‌ترین یافته‌ها و نتیجه‌گیری‌ها.", "items": {"type": "string"}}
                        },
                        "required": ["نام_شرکت", "نام_حسابرس", "دوره_مالی", "نوع_اظهارنظر", "سطح_ریسک_کلی_بنا_به_گزارش", "جزییات_سطح_ریسک_تعیین_شده", "نکات_کلیدی_و_نتیجه_گیری"]
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
                                    "نوع_دلیل": {"type": "string", "enum": ["محدودیت در رسیدگی", "انحراف از استانداردهای حسابداری", "سایر"]}
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
                                    "ارجاع": {
                                        "type": "object",
                                        "description": "ارجاع به شماره بند و صفحه مربوطه در گزارش اصلی.",
                                        "properties": {
                                            "شماره_بند": {"type": "string", "description": "شماره بند مربوطه در گزارش حسابرس مستقل و بازرس قانونی .بین بند ها , قرار بده مانند ۲,۶"},
                                        "شماره_صفحه": {"type": "string", "description": "شماره صفحه مربوطه در گزارش حسابرس مستقل و بازرس قانونی.چنانچه این مورد در چند بند به ان اشاره شده صفحات منطبق با بند را به ترتیب بند برگردان بین صفحات , قرار بده مانند ۱,۵"}
                                        },
                                        "required": ["شماره_بند", "شماره_صفحه"]
                                    },
                                    "عنوان": {"type": "string"},
                                    "شرح": {"type": "string"},
                                    "ریسک_برجسته_شده": {"type": "string"}
                                    },
                                    "required": ["ارجاع", "عنوان", "شرح", "ریسک_برجسته_شده"]
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
                                    "ارجاع": {
                                        "type": "object",
                                        "description":  "ارجاع به شماره بند و صفحه مربوطه در گزارش اصلی.",
                                        "properties": {
                                            "شماره_بند": {"type": "string", "description": "شماره بند مربوطه در گزارش حسابرس مستقل و بازرس قانونی .بین بند ها , قرار بده مانند ۲,۶"},
                                        "شماره_صفحه": {"type": "string", "description": "شماره صفحه مربوطه در گزارش حسابرس مستقل و بازرس قانونی.چنانچه این مورد در چند بند به ان اشاره شده صفحات منطبق با بند را به ترتیب بند برگردان بین صفحات , قرار بده مانند ۱,۵"}
                                        },
                                        "required": ["شماره_بند", "شماره_صفحه"]
                                    },
                                    "عنوان_تخلف": {"type": "string"},
                                    "شرح": {"type": "string"},
                                    "مبانی_قانونی_و_است
