import streamlit as st
import pandas as pd
import selenium.webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.common.by
import selenium.webdriver.common.keys
import selenium.webdriver.support.ui
import selenium.webdriver.support.expected_conditions
def get_driver():
    """Setup Chrome Driver"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Keep this commented to see the browser work
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    # This argument is crucial for Google Maps to load correctly in automation
    chrome_options.add_argument("--lang=en-GB") 
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def analyze_shortcoming(website_url):
    """Analyze the website status"""
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

def scrape_google_maps(city, category, limit):
    driver = get_driver()
    search_query = f"{category} in {city}"
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    # 1. USE STANDARD GOOGLE MAPS URL (English)
    url = "https://www.google.com/maps?hl=en"
    status_text.info(f"🌍 Opening Google Maps ({url})...")
    driver.get(url)
    
    # 2. HANDLE POPUPS & FIND SEARCH BOX
    try:
        wait = WebDriverWait(driver, 10)
        
        # A. Try to close "Sign in" or "Cookie" popups if they exist
        try:
            # Look for common "Accept" or "Keep using web" buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                if "Accept all" in btn.get_attribute("aria-label") or "Agree" in btn.text:
                    btn.click()
                    time.sleep(2)
        except:
            pass

        # B. Find Search Box (Try 3 different IDs)
        try:
            # Primary Method (Standard ID)
            search_box = wait.until(EC.element_to_be_clickable((By.ID, "searchboxinput")))
        except:
            try:
                # Backup Method 1 (By Name)
                search_box = driver.find_element(By.NAME, "q")
            except:
                # Backup Method 2 (Any Input field)
                search_box = driver.find_element(By.TAG_NAME, "input")

        search_box.clear()
        search_box.send_keys(search_query)
        # Use the search button click instead of Enter key (sometimes Enter is blocked)
        try:
            search_btn = driver.find_element(By.ID, "searchbox-searchbutton")
            search_btn.click()
        except:
            search_box.send_keys(Keys.ENTER)
            
        status_text.info(f"🔍 Searching for: {search_query}")
        
    except Exception as e:
        st.error(f"❌ Search Error: {e}")
        # DEBUG: Take a screenshot to see what is blocking it
        driver.save_screenshot("debug_search_fail.png")
        st.warning("Check 'debug_search_fail.png' in your folder to see what the bot sees.")
        driver.quit()
        return pd.DataFrame()
        
    time.sleep(5) # Wait for results list

    # 3. SCROLL SIDEBAR (Feed)
    try:
        # Wait specifically for the Feed (List of results)
        sidebar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
        )
        status_text.info(f"📜 Scrolling results...")
        
        # Scroll Loop
        for _ in range(0, int(limit/2)): # Scroll enough times
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", sidebar)
            time.sleep(2)
            # Check count
            cards = sidebar.find_elements(By.CSS_SELECTOR, "div[role='article']")
            if len(cards) >= limit:
                break
                
    except Exception as e:
        status_text.warning("⚠️ Could not scroll sidebar (Might be fewer results).")

    # 4. EXTRACT DATA
    collected_data = []
    cards = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
    
    status_text.info(f"🔍 Extracting {len(cards[:limit])} businesses...")
    
    for i, card in enumerate(cards[:limit]):
        try:
            name = card.get_attribute("aria-label")
            if not name:
                continue 

            # A. Basic Info from List
            rating = "N/A"
            reviews = "0"
            try:
                # Get all text from card to parse rating
                text_lines = card.text.split('\n')
                for line in text_lines:
                    # Look for pattern like "4.5(500)" or "4.5 stars"
                    if "(" in line and ")" in line and any(c.isdigit() for c in line):
                         # Simple parser
                         parts = line.split("(")
                         rating = parts[0].strip()
                         reviews = parts[1].split(")")[0].replace(",", "")
                         break
            except:
                pass

            # B. Click for Details (Phone/Website)
            try:
                card.click()
                time.sleep(1.5)
            except:
                pass
            
            phone = "Not Available"
            website = "N/A"
            address = "N/A"
            
            # C. Scrape Sidebar Panel
            try:
                # Address
                try:
                    btns = driver.find_elements(By.CSS_SELECTOR, "button[data-item-id='address']")
                    if btns: address = btns[0].get_attribute("aria-label").replace("Address: ", "")
                except: pass

                # Phone
                try:
                    btns = driver.find_elements(By.CSS_SELECTOR, "button[data-item-id*='phone']")
                    if btns: phone = btns[0].get_attribute("aria-label").replace("Phone: ", "")
                except: pass

                # Website
                try:
                    links = driver.find_elements(By.CSS_SELECTOR, "a[data-item-id='authority']")
                    if links: website = links[0].get_attribute("href")
                except: pass
            except:
                pass

            # D. Analysis
            priority = "Normal"
            try:
                if int(reviews) > 50 and (website == "N/A" or "business.site" in website):
                    priority = "🔥 HOT LEAD"
            except: pass

            shortcoming, service = analyze_shortcoming(website)

            collected_data.append({
                "Business Name": name,
                "Phone": phone,
                "Website": website,
                "Rating": rating,
                "Reviews": reviews,
                "Priority": priority,
                "Region": city,
                "Shortcoming": shortcoming,
                "Potential Service": service
            })
            
            progress_bar.progress((i + 1) / limit)
            
        except Exception as e:
            continue
            
    driver.quit()
    status_text.success("✅ Done!")
    return pd.DataFrame(collected_data)
# --- STREAMLIT UI ---
st.set_page_config(page_title="G-Maps Lead Scraper", page_icon="📍")
st.title("📍 Google Maps Lead Scraper")
st.markdown("A stable alternative to Justdial for finding business leads.")

c1, c2, c3 = st.columns(3)
city = c1.selectbox("Region", ["Chandigarh", "Mohali", "Ludhiana", "Delhi"])
cat = c2.selectbox("Category", ["Restaurants", "Gyms", "Hotels", "Dentists"])
limit = c3.slider("Leads", 5, 30, 10)

if st.button("🚀 Find Leads on Maps"):
    with st.spinner("Scraping Google Maps... This takes a few seconds per lead..."):
        df = scrape_google_maps(city, cat, limit)
        if not df.empty:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download CSV", csv, "leads.csv", "text/csv")
        else:
            st.error("No leads found. Try a different category.")