import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random

# --- CONFIGURATION ---
ICON_MAP = {
    'dc': '+', 'fe': '(', 'hg': ')', 'ba': '-',
    'acb': '0', 'yz': '1', 'wx': '2', 'vu': '3',
    'ts': '4', 'rq': '5', 'po': '6', 'nm': '7',
    'lk': '8', 'ji': '9'
}

# 1. DELETE this import at the top if you see it:
# from webdriver_manager.chrome import ChromeDriverManager 

def get_driver():
    """Setup Chrome Driver (NATIVE MODE)"""
    chrome_options = Options()
    
    # Keep these settings to look like a human
    chrome_options.add_argument("--start-maximized") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # --- THE CHANGE IS HERE ---
    # Old line (Delete this):
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # NEW LINE (Use this):
    # Selenium 4.10+ can find the driver automatically without the Manager tool.
    driver = webdriver.Chrome(options=chrome_options)
    
    # Stealth settings
    try:
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
    except:
        pass
        
    return driver

def decode_phone(element):
    """Decode Justdial Phone Icons"""
    phone_digits = []
    try:
        # Justdial structure for phones often changes. This targets the common wrapper.
        # We look for spans with class 'mobilesv'
        icons = element.find_elements(By.CLASS_NAME, "mobilesv")
        for icon in icons:
            classes = icon.get_attribute("class").split()
            for c in classes:
                if c in ICON_MAP:
                    phone_digits.append(ICON_MAP[c])
        return "".join(phone_digits)
    except:
        return ""

def analyze_shortcoming(website_url):
    """
    Real Logic to determine the problem (Shortcoming)
    based on the actual URL found.
    """
    if not website_url:
        return "No Website Found", "Create Professional Website"
    
    url_lower = website_url.lower()
    
    # Check for 'Fake' or 'Sub-standard' websites
    if "facebook.com" in url_lower:
        return "Using Facebook as Website", "Build Dedicated .com Site"
    elif "instagram.com" in url_lower:
        return "Using Instagram as Website", "Build Dedicated .com Site"
    elif "justdial.com" in url_lower:
        return "Redirects to Justdial Profile", "Create Own Brand Identity"
    elif "business.site" in url_lower:
        return "Using Free Google Site (Closing Soon)", "Migrate to WordPress/Custom"
    elif "wix.com" in url_lower or "wordpress.com" in url_lower:
        return "Using Free Subdomain", "Upgrade to Professional Domain"
    elif "http://" in url_lower and "https://" not in url_lower:
        return "Not Secure (No SSL)", "Fix Security & Trust"
    else:
        # If they have a real site, we assume optimization is needed
        return "Website Exists (Audit Needed)", "Redesign / SEO / Speed"

def scrape_leads_pagination(city, category, limit):
    driver = get_driver()
    url = f"https://www.justdial.com/{city}/{category}"
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    status_text.info(f"🌐 Opening {url}...")
    driver.get(url)
    
    # --- CHANGE: THE "HUMAN HELP" PAUSE ---
    st.warning("⚠️ WAITING 30 SECONDS... If you see a CAPTCHA or blank page in the popup window, please fix it manually now!")
    time.sleep(30) # Force wait for slow internet / manual captcha solving
    
    status_text.info("✅ Time up! Attempting to read data now...")

    collected_data = []
    
    # 2. SCROLLING
    status_text.info(f"📜 Scrolling to load {limit} results...")
    for _ in range(int(limit/5) + 2):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) # Increased wait between scrolls
    
  # ... (Keep Step 1 and Step 2 as they were) ...
    
    # 3. THE "LINK-BASED" EXTRACTION STRATEGY
    all_links = driver.find_elements(By.TAG_NAME, "a")
    
    status_text.info(f"🔍 Scanning {len(all_links)} links...")

    unique_businesses = set()
    count = 0
    
    for link in all_links:
        if count >= limit:
            break
            
        try:
            href = link.get_attribute("href")
            title = link.text.strip()
            
            # Smart Filter
            if (href and city in href and 
                len(title) > 3 and 
                "Review" not in title and 
                "Rating" not in title and 
                "javascript" not in href):
                
                if title in unique_businesses:
                    continue
                unique_businesses.add(title)

                name = title
                
                # --- FIND PARENT CARD ---
                try:
                    # Go up 3 levels to find the container
                    parent_card = link.find_element(By.XPATH, "./../../..")
                except:
                    continue # Skip if card structure is broken

                # --- FIND WEBSITE ---
                website_url = ""
                try:
                    card_links = parent_card.find_elements(By.TAG_NAME, "a")
                    for cl in card_links:
                        c_href = cl.get_attribute("href")
                        if (c_href and "http" in c_href and 
                            "justdial.com" not in c_href and 
                            "google.com" not in c_href):
                            website_url = c_href
                            break
                except:
                    pass

                # --- NEW: PHONE NUMBER CLICKER ---
                phone = "Not Found"
                try:
                    # 1. Look for the "Show Number" button inside this card
                    show_btn = parent_card.find_element(By.XPATH, ".//*[contains(text(), 'Show Number')]")
                    
                    # 2. Click it using JavaScript (Bypasses overlays)
                    driver.execute_script("arguments[0].click();", show_btn)
                    
                    # 3. Wait a split second for text to change
                    time.sleep(1)
                    
                    # 4. Read the new text
                    # Often the button text ITSELF changes to the number
                    if show_btn.text != "Show Number":
                        phone = show_btn.text
                    else:
                        # If text didn't change, maybe a popup opened?
                        phone = "Login Required to View"
                        
                except:
                    # If "Show Number" button is missing, maybe the old icon format is there?
                    phone = decode_phone(parent_card)
                    if not phone:
                        phone = "Hidden"

                # Analyze
                shortcoming, service = analyze_shortcoming(website_url)

                collected_data.append({
                    "Business Category": category,
                    "Region": city,
                    "Business Name": name,
                    "Existing Website": "Yes" if website_url else "No",
                    "Website URL": website_url if website_url else "N/A",
                    "Website Shortcomings": shortcoming,
                    "Potential Services": service,
                    "Contact Info": phone,
                    "Status": "New Lead"
                })
                
                count += 1
                progress_bar.progress(count / limit)
                
        except Exception as e:
            continue

    driver.quit()
    
    if not collected_data:
        st.error("❌ Still failed. Try searching Google Maps instead (It is easier to scrape).")
    else:
        status_text.success("✅ Success!")
        
    return pd.DataFrame(collected_data)
# --- APP UI ---
st.set_page_config(page_title="Lead Scraper Pro", layout="wide")

st.title("🕵️ Lead Generation Dashboard")
st.markdown("Fetch **real-time data** from directories. Analysis is based on actual link availability.")

col1, col2, col3 = st.columns(3)

with col1:
    region = st.selectbox("Select Region", ["Chandigarh", "Mohali", "Panchkula", "Ludhiana", "Shimla", "Delhi"])

with col2:
    category = st.selectbox("Business Category", ["Restaurants", "Hotels", "Gyms", "Dentists", "Real Estate", "Jewellers"])

with col3:
    # THE SLIDER YOU REQUESTED
    limit = st.select_slider("Results to Fetch", options=[10, 20, 30, 40, 50], value=10)

if st.button("🚀 Start Scraping", use_container_width=True):
    with st.spinner("Initializing Scraper... This may take 30-60 seconds for 50 results..."):
        df = scrape_leads_pagination(region, category, limit)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # CSV Download
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Excel/CSV",
                data=csv,
                file_name=f"Leads_{region}_{category}.csv",
                mime="text/csv",
            )
        else:
            st.error("No results found. The directory might be blocking automated access. Try again in 5 minutes.")