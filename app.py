import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="إدارة حجوزات ", page_icon="🏡", layout="centered")

st.markdown("""
    <style>
    .reportview-container { direction: rtl; text-align: right; }
    button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

DATA_FILE = "farm_bookings.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        required_cols = ["اسم المستأجر", "رقم الجوال", "قيمة الإيجار", "العربون", "المتبقي", "يوم الحجز", "حالة الحجز"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        return df
    else:
        return pd.DataFrame(columns=["اسم المستأجر", "رقم الجوال", "قيمة الإيجار", "العربون", "المتبقي", "يوم الحجز", "حالة الحجز"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_bookings = load_data()

st.title("🏡 البديع")
st.write("مرحباً بك! يمكنك إدارة وتسجيل الحجوزات من هنا.")

choice = st.radio("اختر الإجراء:", ["📝 تسجيل حجز جديد", "📅 استعراض وإدارة الحجوزات"], horizontal=True)

if choice == "📝 تسجيل حجز جديد":
    st.subheader("إدخال بيانات المستأجر الجديد")
    
    with st.form(key='booking_form', clear_on_submit=True):
        name = st.text_input("اسم المستأجر *")
        phone = st.text_input("رقم الجوال *")
        
        col1, col2 = st.columns(2)
        with col1:
            total_price = st.number_input("قيمة الإيجار (ريال)", min_value=0.0, step=50.0)
            deposit = st.number_input("العربون (ريال)", min_value=0.0, step=50.0)
        with col2:
            remaining = total_price - deposit
            st.write(f"**المتبقي تلقائياً:** {remaining} ريال")
            booking_date = st.date_input("يوم الحجز", value=datetime.now())
        
        status = st.selectbox("حالة الحجز المبدئية", ["باقي (قادم)", "تم وانتهى"])
        
        submit_button = st.form_submit_button(label='حفظ الحجز 💾')
        
        if submit_button:
            if name == "" or phone == "":
                st.error("الرجاء كتابة اسم المستأجر ورقم الجوال!")
            else:
                new_data = pd.DataFrame([{
                    "اسم المستأجر": name,
                    "رقم الجوال": f"'{phone}",
                    "قيمة الإيجار": total_price,
                    "العربون": deposit,
                    "المتبقي": remaining,
                    "يوم الحجز": str(booking_date),
                    "حالة الحجز": status
                }])
                df_bookings = pd.concat([df_bookings, new_data], ignore_index=True)
                save_data(df_bookings)
                st.success(f"تم تسجيل حجز لـ {name} بنجاح! 🎉")

elif choice == "📅 استعراض وإدارة الحجوزات":
    st.subheader("كل الحجوزات المسجلة")
    
    if df_bookings.empty:
        st.info("لا توجد أي حجوزات مسجلة حتى الآن.")
    else:
        search_query = st.text_input("🔍 ابحث باسم المستأجر أو رقم جواله:")
        
        df_display = df_bookings.copy()
        if search_query:
            df_display = df_display[df_display['اسم المستأجر'].str.contains(search_query, na=False) | df_display['رقم الجوال'].str.contains(search_query, na=False)]
        
        st.write("---")
        for index, row in df_display.iterrows():
            color = "🟢" if row['حالة الحجز'] == "تم وانتهى" else "🟡"
            
            with st.expander(f"{color} {row['اسم المستأجر']} - بتاريخ: {row['يوم الحجز']}"):
                cleaned_phone = str(row['رقم الجوال']).replace("'", "")
                st.write(f"**رقم الجوال:** {cleaned_phone}")
                st.write(f"**قيمة الإيجار:** {row['قيمة الإيجار']} ريال | **العربون:** {row['العربون']} ريال | **المتبقي:** {row['المتبقي']} ريال")
                st.write(f"**الحالة الحالية:** {row['حالة الحجز']}")
                
                if row['حالة الحجز'] == "باقي (قادم)":
                    if st.button(f"تعديل إلى: تم وانتهى ✅", key=f"btn_{index}"):
                        df_bookings.at[index, 'حالة الحجز'] = "تم وانتهى"
                        save_data(df_bookings)
                        st.rerun()
                else:
                    if st.button(f"إعادة إلى: باقي (قادم) ⏳", key=f"btn_{index}"):
                        df_bookings.at[index, 'حالة الحجز'] = "باقي (قادم)"
                        save_data(df_bookings)
                        st.rerun()