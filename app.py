import streamlit as st
import sqlite3
import time
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

# إعداد قاعدة البيانات
conn = sqlite3.connect("inventory_final.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS items 
                  (id INTEGER PRIMARY KEY, name TEXT, image_path TEXT, x REAL, y REAL, steps INTEGER)''')
conn.commit()

st.title("📍 مساعد الذاكرة البصري")

tab1, tab2 = st.tabs(["➕ إضافة غرض", "🔍 بحث وتوجيه"])

with tab1:
    source = st.radio("اختر مصدر الصورة:", ("رفع ملف من الهاتف", "استخدام الكاميرا مباشرة"))
    
    picture = None
    if source == "استخدام الكاميرا مباشرة":
        picture = st.camera_input("التقط صورة للغرض")
        st.caption("ملاحظة: إذا لم تظهر الكاميرا، تأكد من استخدام رابط آمن أو إعطاء إذن للمتصفح.")
    else:
        picture = st.file_uploader("اختر صورة من الاستوديو", type=["jpg", "png", "jpeg"])

    if picture:
        img = Image.open(picture)
        img_path = f"img_{int(time.time())}.jpg"
        img.save(img_path)
        
        st.write("اضغط على مكان الغرض في الصورة:")
        # تصغير الصورة للعرض المناسب على الموبايل
        value = streamlit_image_coordinates(img, key="add_coords")
        
        if value:
            name = st.text_input("اسم الغرض:")
            steps = st.number_input("المسافة بالخطوات عن المدخل:", min_value=0)
            if st.button("حفظ الآن"):
                cursor.execute("INSERT INTO items (name, image_path, x, y, steps) VALUES (?, ?, ?, ?, ?)", 
                               (name.lower(), img_path, value['x'], value['y'], steps))
                conn.commit()
                st.success("تم الحفظ!")

with tab2:
    search = st.text_input("ابحث عن مكان غرضك:")
    if search:
        cursor.execute("SELECT * FROM items WHERE name LIKE ?", ('%' + search.lower() + '%',))
        res = cursor.fetchone()
        if res:
            st.info(f"المكان يبعد {res[5]} خطوات تقريباً")
            st.image(res[2], caption=f"مكان {res[1]}")