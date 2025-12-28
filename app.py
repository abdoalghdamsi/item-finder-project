import streamlit as st
import sqlite3
import time
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

# إعداد قاعدة البيانات
conn = sqlite3.connect("inventory_final.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS items 
                  (id INTEGER PRIMARY KEY, name TEXT, image_path TEXT, x REAL, y REAL, steps INTEGER)''')
conn.commit()

st.set_page_config(page_title="مساعد الذاكرة البصري", layout="centered")
st.title("📍 مساعد الذاكرة البصري الذكي")


if total_count > 0:
    cursor.execute("SELECT SUM(steps) FROM items")
    total_steps = cursor.fetchone()[0]
    st.sidebar.info(f"🚶 مشيت {total_steps} خطوة لتخزين هذه الأغراض!")
tab1, tab2 = st.tabs(["➕ إضافة غرض جديد", "🔍 البحث عن غرض"])

# إحصائيات سريعة في القائمة الجانبية
st.sidebar.header("📊 إحصائيات الذاكرة")
cursor.execute("SELECT COUNT(*) FROM items")
total_count = cursor.fetchone()[0]
st.sidebar.metric("إجمالي الأغراض", total_count)

with tab1:
    source = st.radio("اختر مصدر الصورة:", ("رفع ملف من الاستوديو", "استخدام الكاميرا"))
    
    picture = st.camera_input("التقط صورة") if source == "استخدام الكاميرا" else st.file_uploader("اختر صورة", type=["jpg", "png", "jpeg"])

    if picture:
        img = Image.open(picture)
        img_path = f"img_{int(time.time())}.jpg"
        
        st.write("### 👈 انقر على مكان الغرض في الصورة:")
        
        # عرض الصورة والتقاط الإحداثيات
        coords = streamlit_image_coordinates(img, key="img_input")
        
        if coords:
            # رسم علامة مؤقتة للتوضيح للمستخدم أنه تم النقر
            draw = ImageDraw.Draw(img)
            r = 15 # حجم الدائرة
            draw.ellipse((coords['x']-r, coords['y']-r, coords['x']+r, coords['y']+r), fill="red", outline="white", width=3)
            st.image(img, caption="تم تحديد الموقع بالعلامة الحمراء 🔴")
            
            # رسالة التنبيه المنبثقة
            st.toast(f"تم تحديد الإحداثيات بنجاح: ({coords['x']}, {coords['y']})", icon="✅")
            
            # مدخلات البيانات
            with st.expander("📝 أكمل تفاصيل الحفظ", expanded=True):
                name = st.text_input("ما هو اسم هذا الغرض؟")
                steps = st.number_input("كم خطوة يبعد عن الباب؟", min_value=0)
                
                if st.button("حفظ في الذاكرة"):
                    if name:
                        img.save(img_path) # حفظ الصورة مع العلامة الحمراء
                        cursor.execute("INSERT INTO items (name, image_path, x, y, steps) VALUES (?, ?, ?, ?, ?)", 
                                       (name.lower(), img_path, coords['x'], coords['y'], steps))
                        conn.commit()
                        st.success(f"تم حفظ '{name}' بنجاح!")
                        st.balloons() # بالونات احتفالية عند الحفظ
                    else:
                        st.error("يرجى كتابة اسم الغرض أولاً")

with tab2:
    search = st.text_input("🔍 ابحث عن غرضك:")
    if search:
        cursor.execute("SELECT * FROM items WHERE name LIKE ?", ('%' + search.lower() + '%',))
        res = cursor.fetchone()
        if res:
            st.success(f"وجدته! '{res[1]}' موجود هنا:")
            st.info(f"👣 التوجيه: تحرك {res[5]} خطوات من المدخل.")
            st.image(res[2], use_container_width=True)
        else:
            st.error("عذراً، هذا الغرض غير مسجل في الذاكرة.")

