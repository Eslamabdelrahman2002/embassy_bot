# embassy_bot.py
import os, time, requests, traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")

USER_DATA = {
    "Nachname": "SHABARA", "Vorname": "AMMAR", "Geburtsdatum": "06.01.1999",
    "Reisepass": "A04299704", "Tel": "01555227126", "Email": "amarshabara57@gmail.com"
}

def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ CRITICAL: BOT_TOKEN or CHAT_ID not set")
        return
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print(f"✅ Telegram: {text[:60]}...")
    except Exception as e:
        print("❌ Telegram error:", e)

def create_driver():
    options = Options()
    # new headless مناسب لـ Chromium الحديث
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # حدد مسار الكروميوم حسب ديبيان/سليم
    for path in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
        if os.path.exists(path):
            options.binary_location = path
            print(f"ℹ️ Using Chromium at: {path}")
            break

    # حدد مسار chromedriver
    driver_path = None
    for path in ("/usr/bin/chromedriver", "/usr/lib/chromium/chromedriver", "/usr/local/bin/chromedriver"):
        if os.path.exists(path):
            driver_path = path
            print(f"ℹ️ Using Chromedriver at: {path}")
            break

    if driver_path:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # fallback لسيلينيوم مانجر (لو متاح)
        print("⚠️ Chromedriver path not found, trying Selenium Manager…")
        driver = webdriver.Chrome(options=options)
    return driver

def attempt_to_book(driver):
    try:
        print("🚀 Attempting to book...")
        available_slot = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'Termin')]"))
        )
        available_slot.click()

        print("📝 Filling personal data...")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, "Nachname"))).send_keys(USER_DATA["Nachname"])
        driver.find_element(By.NAME, "Vorname").send_keys(USER_DATA["Vorname"])
        driver.find_element(By.NAME, "Geburtsdatum").send_keys(USER_DATA["Geburtsdatum"])
        driver.find_element(By.NAME, "Reisepass").send_keys(USER_DATA["Reisepass"])
        driver.find_element(By.NAME, "Tel").send_keys(USER_DATA["Tel"])
        driver.find_element(By.NAME, "Email").send_keys(USER_DATA["Email"])

        print("✅ Data entry ok.")
        send_telegram_message("🎉 Appointment found & data filled. Solve CAPTCHA if needed.")
        time.sleep(300)
        return True
    except Exception as e:
        print("❌ Auto-booking failed:", e)
        send_telegram_message(f"❌ Auto-booking failed: {e}")
        return False

def check_appointments_once():
    driver = create_driver()
    booked = False
    try:
        print("🌐 Navigating...")
        driver.get("https://appointment.bmeia.gv.at/")

        Select(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "Office")))).select_by_visible_text("KAIRO")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        Select(WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "CalendarId")))).select_by_visible_text("Aufenthaltsbewilligung Student (nur Bachelor)")
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Next']"))).click()
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Next']"))).click()

        print("🔍 Checking appointments page...")
        time.sleep(2)

        if "no appointments available" in driver.page_source.lower():
            print("⚠️ No appointments available.")
        else:
            print("🎉 Appointment found!")
            send_telegram_message("🎉 Appointment found! Trying to auto-book…")
            booked = attempt_to_book(driver)
    finally:
        if not booked:
            driver.quit()
    return booked

def main():
    send_telegram_message("🚀 Debugging bot started successfully.")
    while True:
        print("\n" + "="*50)
        print(f"🔍 Starting new check at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        if check_appointments_once():
            print("✅ Booking attempted. Stopping.")
            send_telegram_message("✅ Bot stopping after booking attempt.")
            break
        wait_time = 300
        print(f"⏳ Retrying in {wait_time//60} min...")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()

