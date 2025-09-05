# -*- coding: utf-8 -*-
import time
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ==============================================================================
# # بيانات التليجرام (تأكد من صحتها)
# # ==============================================================================
# # استخدم التوكن والـ ID الخاصين بك
# BOT_TOKEN = "8494526180:AAExdDSIm3x6E-jSPbLeZfVjzvOHWCmXOmc"
# CHAT_ID = "5946798369"

# ==============================================================================
# بياناتك الشخصية (تأكد من صحتها)
# ==============================================================================
# -*- coding: utf-8 -*-
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# ==============================================================================
# بيانات التليجرام
# ==============================================================================
BOT_TOKEN = "8494526180:AAExdDSIm3x6E-jSPbLeZfVjzvOHWCmXOmc"
CHAT_ID = "5946798369"

# ==============================================================================
# بياناتك الشخصية
# ==============================================================================
USER_DATA = {
    "Nachname": "SHABARA",
    "Vorname": "AMMAR",
    "Geburtsdatum": "06.01.1999",
    "Reisepass": "A04299704",
    "Tel": "01555227126",
    "Email": "amarshabara57@gmail.com"
}


# ------------------------------------------------------------------------------
# Selenium Driver (Headless)
# ------------------------------------------------------------------------------
def create_driver():
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)


# ------------------------------------------------------------------------------
# Telegram notification
# ------------------------------------------------------------------------------
def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data, timeout=10)
        print(f"✅ تم إرسال إشعار تليجرام: '{text}'")
    except Exception as e:
        print(f"❌ مشكلة في إرسال رسالة التليجرام: {e}")


# ------------------------------------------------------------------------------
# محاولة الحجز
# ------------------------------------------------------------------------------
def attempt_to_book(driver):
    try:
        print("🚀 جارٍ محاولة حجز أول موعد متاح...")
        available_slot = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'Termin')]"))
        )
        available_slot.click()
        
        print("📝 جارٍ إدخال البيانات الشخصية...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "Nachname"))
        ).send_keys(USER_DATA["Nachname"])
        driver.find_element(By.NAME, "Vorname").send_keys(USER_DATA["Vorname"])
        driver.find_element(By.NAME, "Geburtsdatum").send_keys(USER_DATA["Geburtsdatum"])
        driver.find_element(By.NAME, "Reisepass").send_keys(USER_DATA["Reisepass"])
        driver.find_element(By.NAME, "Tel").send_keys(USER_DATA["Tel"])
        driver.find_element(By.NAME, "Email").send_keys(USER_DATA["Email"])

        print("✅ تم إدخال البيانات بنجاح.")
        send_telegram_message(
            "🎉 تم العثور على موعد وملء بياناتك بنجاح 🎉\n"
            "الخطوة الأخيرة عليك الآن!\n"
            "اذهب إلى نافذة المتصفح المفتوحة، قم بحل الكابتشا (التحقق الأمني) واضغط على إرسال لإتمام الحجز.\n"
            "لديك 5 دقائق."
        )
        time.sleep(300)
        return True

    except Exception as e:
        print(f"❌ فشلت عملية الحجز التلقائي: {e}")
        send_telegram_message("❌ فشل الحجز التلقائي. يرجى المحاولة يدويًا بسرعة!")
        return False


# ------------------------------------------------------------------------------
# فحص المواعيد
# ------------------------------------------------------------------------------
def check_appointments_once():
    driver = create_driver()
    driver.maximize_window()
    appointment_booked = False
    
    try:
        print("🌐 جارٍ فتح الموقع والتنقل بين الصفحات...")
        driver.get("https://appointment.bmeia.gv.at/")

        # الخطوة 1: اختيار المكتب (KAIRO)
        Select(WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "Office")))).select_by_visible_text("KAIRO")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        
        # الخطوة 2: اختيار نوع التأشيرة
        Select(WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "CalendarId")))).select_by_visible_text("Aufenthaltsbewilligung Student (nur Bachelor)")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        
        # الخطوة 3 و 4
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Next']"))).click()
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Next']"))).click()
        
        print("🔍 جارٍ فحص صفحة المواعيد...")
        time.sleep(2)

        if "no appointments available" in driver.page_source.lower():
            print("--- ⚠️ لا يوجد مواعيد متاحة حاليًا ---")
        else:
            print("🎉🎉🎉 تم العثور على موعد متاح! 🎉🎉🎉")
            send_telegram_message("🎉 تم العثور على موعد! جارٍ محاولة الحجز تلقائيًا...")
            appointment_booked = attempt_to_book(driver)

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")
        send_telegram_message("❌ حدث خطأ في البوت. قد يكون الموقع تغير أو هناك مشكلة في الاتصال.")
    finally:
        if not appointment_booked:
            driver.quit()
    return appointment_booked


# ------------------------------------------------------------------------------
# الحلقة الرئيسية
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    send_telegram_message("🚀 تم تشغيل بوت حجز المواعيد بنجاح.")
    while True:
        print("\n" + "="*50)
        print("🔍 بدء دورة فحص جديدة...")
        found_and_booked = check_appointments_once()
        if found_and_booked:
            print("✅ تمت محاولة الحجز بنجاح. سيتم إيقاف البوت الآن.")
            send_telegram_message("✅ تم إيقاف البوت بعد محاولة الحجز.")
            break
        
        wait_time = 300
        print(f"⏳ لا يوجد مواعيد. سيتم إعادة المحاولة بعد {wait_time/60:.0f} دقائق...")
        time.sleep(wait_time)
