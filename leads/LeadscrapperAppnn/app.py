import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# --- SETUP DRIVER (PERSISTENT) ---
def get_driver():
    """Setup Chrome Driver if not already running"""
    if 'driver' not in st.session_state or st.session_state.driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--lang=en-GB")
        
        # Initialize and store in session state
        driver = webdriver.Chrome(options=chrome_options)
        st.session_state.driver = driver
    return st.session_state.driver

def close_driver():
    if 'driver' in st.session_state and st.session_state.driver:
        st.session_state.driver.quit()
        st.session_state.driver = None

# --- ANALYSIS LOGIC ---
def analyze_shortcoming(website_url):
    if not website_url or website_url == "N/A":
        return "No Website Found", "Create Professional Website"
    
    url_lower = website_url.lower()
    if "business.site" in url_lower:
        return "Using Free Google Site (Closing Soon)", "Migrate to Real .com Domain"
    elif "facebook.com" in url_lower or "instagram.com" in url_lower:
        return "Social Media Profile Only", "Build Dedicated Brand Website"
    elif "http://" in url_lower and "https://" not in url_lower:
        return "Not Secure (No SSL)", "Security Update Needed"
    else:
        return "Website Exists", "Offer Redesign / SEO"

# --- SCRAPING LOGIC ---
def scrape_current_view(limit):
    driver = get_driver()
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    status_text.info("🔍 Looking for results in the open window...")
    
    # 1. FIND SIDEBAR
    try:
        # Generic selector for the scrollable list
        sidebar = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
    except:
        st.error("❌ Could not find the results list! Make sure you have searched for something (e.g., 'Gyms in Delhi') and the list is visible on the left.")
        return pd.DataFrame()

    # 2. SCROLL LOOP
    status_text.info(f"📜 Scrolling to load {limit} leads...")
    scrolled_cards = []
    attempts = 0
    
    while len(scrolled_cards) < limit and attempts < 20:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
        time.sleep(1.5)
        scrolled_cards = sidebar.find_elements(By.CSS_SELECTOR, "div[role='article']")
        attempts += 1
    
    # 3. EXTRACT
    status_text.info(f"⛏️ Extracting data from {len(scrolled_cards)} businesses...")
    collected_data = []
    
    for i, card in enumerate(scrolled_cards[:limit]):
        try:
            # Basic Parse
            text_lines = card.text.split('\n')
            name = card.get_attribute("aria-label")
            if not name: continue
            
            rating, reviews = "N/A", "0"
            for line in text_lines:
                if "(" in line and ")" in line and any(c.isdigit() for c in line):
                    parts = line.split("(")
                    rating = parts[0].strip()
                    reviews = parts[1].split(")")[0].replace(",", "")
                    break
            
            # Click for Details (Fast Click)
            try:
                card.click()
                time.sleep(1) 
            except: pass

            phone = "Not Available"
            website = "N/A"
            address = "N/A"
            
            # Scrape Visible Details
            try:
                # Address
                x = driver.find_elements(By.CSS_SELECTOR, "button[data-item-id='address']")
                if x: address = x[0].get_attribute("aria-label").replace("Address: ", "")
                
                # Phone
                x = driver.find_elements(By.CSS_SELECTOR, "button[data-item-id*='phone']")
                if x: phone = x[0].get_attribute("aria-label").replace("Phone: ", "")
                
                # Website
                x = driver.find_elements(By.CSS_SELECTOR, "a[data-item-id='authority']")
                if x: website = x[0].get_attribute("href")
            except: pass
            
            # Analysis
            priority = "Normal"
            if reviews.isdigit() and int(reviews) > 50 and (website == "N/A" or "business.site" in website):
                priority = "🔥 HOT LEAD"

            shortcoming, service = analyze_shortcoming(website)

            collected_data.append({
                "Business Name": name,
                "Phone": phone,
                "Website": website,
                "Rating": rating,
                "Reviews": reviews,
                "Priority": priority,
                "Address": address,
                "Shortcoming": shortcoming,
                "Potential Service": service
            })
            progress_bar.progress((i + 1) / limit)
            
        except: continue

    status_text.success("✅ Done!")
    return pd.DataFrame(collected_data)

# --- UI LAYOUT ---
st.set_page_config(page_title="Lead Assistant", page_icon="🤖")
st.title("🤖 Semi-Auto Lead Scraper")
st.markdown("""
**How to use:**
1. Click **'Open Google Maps'**.
2. In the new window, **Type your search** (e.g., "Hotels in Shimla") and press Enter.
3. Once you see the list of businesses, come back here and click **'Scrape Results'**.
""")

col1, col2 = st.columns(2)

with col1:
    if st.button("🌐 1. Open Google Maps"):
        driver = get_driver()
        driver.get("https://www.google.com/maps?hl=en")
        st.success("Browser Opened! Search manually now.")

with col2:
    limit = st.slider("Leads to fetch", 10, 50, 20)
    if st.button("🚀 2. Scrape Results"):
        if 'driver' in st.session_state and st.session_state.driver:
            df = scrape_current_view(limit)
            if not df.empty:
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, "leads.csv", "text/csv")
            else:
                st.warning("No leads extracted. Did you search first?")
        else:
            st.error("Please open the browser first.")

if st.button("❌ Close Browser"):
    close_driver()