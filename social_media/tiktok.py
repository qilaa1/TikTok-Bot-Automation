import time
import os
import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver


def configure_driver():
    """Configure the Chrome WebDriver with mobile emulation."""
    options = Options()
    options.add_argument('--log-level=3')  # Suppress logs
    options.add_argument(f"--user-data-dir={os.getcwd()}\\profile")  # Save session
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"
    }
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    )
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_position(0, 0)
    driver.set_window_size(414, 936)  # Mobile screen resolution
    return driver


def save_cookies(cookies, filename):
    """Save cookies to a file using pickle."""
    try:
        with open(filename, 'wb') as file:
            pickle.dump(cookies, file)
        print(f"Cookies saved successfully to {filename}.")
    except Exception as e:
        print(f"Error saving cookies: {e}")


def load_cookies(filename):
    """Load cookies from a file using pickle."""
    try:
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'rb') as file:
                return pickle.load(file)
        else:
            print(f"No valid cookie file found: {filename}")
            return None
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return None


def login(driver, email, password, cookies=None):
    """Login to TikTok using either cookies or manual login."""
    driver.get("https://www.tiktok.com")

    if cookies:
        # Load cookies into the browser
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("Cookies loaded. Skipping login...")
        driver.refresh()
    else:
        print("No cookies found. Proceeding with manual login.")
        driver.get('https://www.tiktok.com/login/phone-or-email/email')

        # Wait for login page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="text"]'))
        )

        # Type email and password
        driver.find_element(By.XPATH, '//input[@type="text"]').send_keys(email)
        time.sleep(1)
        driver.find_element(By.XPATH, '//input[@type="password"]').send_keys(password)
        time.sleep(1)

        # Submit login form
        driver.find_element(By.XPATH, '//button[@type="submit"]').click()
        time.sleep(5)

    # Save cookies after successful login
    cookies = driver.get_cookies()
    save_cookies(cookies, 'tiktok_cookies.pkl')
    print("Login successful and cookies saved.")
def get_video_and_comment(driver, video_url, keyword_list=["harga", "price", "diskon", "cara beli"]):
    """Get a video from the URL and post a reply to comments based on keywords."""
    driver.get(video_url)
    print(f"Opened video URL: {video_url}")

    try:
        # Wait for the video to load
        video_xpath = '//video'
        video_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, video_xpath))
        )
        print("Video loaded.")

        # Pause video
        try:
            overlay_xpath = '//div[contains(@class, "css-12jr7p2-DivPlayerIconContainer")]'
            overlay_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, overlay_xpath))
            )
            overlay_element.click()
            print("Clicked on overlay to pause video.")
        except:
            driver.execute_script("document.querySelector('video').pause()")
            print("Video paused using JavaScript.")
    except Exception as e:
        print(f"Error while interacting with video: {e}")
        return

    # Click comment button
    try:
        comment_button_xpath = '//*[@id="app"]/div/div[2]/div/div[1]/div/div/div/div[1]/div/div[2]/div/div[1]/div/div[2]'
        comment_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, comment_button_xpath))
        )
        comment_button.click()
        print("Comment button clicked. Pop-up opened.")
    except Exception as e:
        print(f"Error while clicking comment button: {e}")
        return

    # Wait for comments to load
    comments_xpath = '/html/body/div[10]/div[2]/div[2]/div'
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, comments_xpath))
        )
        print("Comments are now visible.")
    except Exception as e:
        print(f"Error waiting for comments to load: {e}")
        return

    # Reload comments after scrolling
    try:
        for _ in range(3):
            driver.execute_script("arguments[0].scrollBy(0, 300);", driver.find_element(By.XPATH, comments_xpath))
            time.sleep(2)
        comments_elements = driver.find_elements(By.XPATH, f"{comments_xpath}/div")
        print(f"Reloaded comments. Found {len(comments_elements)} comments.")
    except Exception as e:
        print(f"Error reloading comments: {e}")
        return

    # Process comments
    try:
        if not comments_elements:
            print("No comments found.")
            return
       # Proses komentar
        # Proses komentar
     
        for idx, comment_element in enumerate(comments_elements):
            try:
                # Scroll to the comment to ensure it is visible
                driver.execute_script("arguments[0].scrollIntoView(true);", comment_element)
                time.sleep(1)
                print(f"Scrolled to comment at index {idx + 1}")

                # Skip input elements
                if "comment-input" in comment_element.get_attribute("outerHTML"):
                    print(f"Skipping input element at index {idx + 1}.")
                    continue

                # Locate the comment text
                try:
                    comment_text_element = comment_element.find_element(
                        By.XPATH, './/p[contains(@data-e2e, "comment-level-1")] | .//div[@data-e2e="comment-text"]'
                    )
                    comment_text = comment_text_element.text.lower()
                    print(f"Comment text at index {idx + 1}: {comment_text}")
                except Exception as e:
                    print(f"No comment text found at index {idx + 1}. Structure: {comment_element.get_attribute('outerHTML')}")
                    continue

                # Locate the username (optional, just for logging)
                try:
                    username_element = comment_element.find_element(
                        By.XPATH, './/span[contains(@data-e2e, "comment-username-1")]'
                    )
                    username = username_element.text.strip()
                    print(f"Username at index {idx + 1}: {username}")
                except Exception:
                    username = "unknown"
                    print(f"Could not locate username for comment at index {idx + 1}.")

                # Check if the comment contains any keywords
                if not any(keyword in comment_text for keyword in keyword_list):
                    print(f"No keywords found in comment at index {idx + 1}. Skipping...")
                    continue

                # Click on the comment text to activate the reply box
                try:
                    comment_text_element.click()
                    print(f"Clicked on comment text to open reply box at index {idx + 1}.")
                    time.sleep(5)  # Penundaan untuk menunggu reply box muncul
                except Exception as e:
                    print(f"Failed to click comment text at index {idx + 1}: {e}")
                    continue
                try:
                    reply_box_xpath = '//div[contains(@class, "DraftEditor-root")]//div[@contenteditable="true"]'
                    reply_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, reply_box_xpath))
                    )

                    # Validasi apakah kotak balasan dapat diakses
                    if reply_box.is_displayed() and reply_box.is_enabled():
                        reply_box.click()
                        response = f"@{username} Terima kasih atas komentarnya!"
                        reply_box.send_keys(response)
                        print(f"Typed response for @{username}: {response}")
                    else:
                        print(f"Reply box not interactable at index {idx + 1}. Skipping...")
                        continue
                except Exception as e:
                    print(f"Error interacting with reply box at index {idx + 1}: {e}")
                    continue

               # Klik tombol Post
                try:
                    # Menggunakan XPath
                    post_button_xpath = '//div[contains(@class, "css-qv0b7z-DivPostButton")]'
                    
                    # Tunggu hingga elemen dapat diklik
                    post_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, post_button_xpath))
                    )
                    
                    # Scroll ke elemen tombol post untuk memastikan terlihat
                    driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
                    time.sleep(1)  # Berikan waktu agar elemen terlihat
                    
                    # Klik tombol
                    post_button.click()
                    print("Successfully clicked the Post button.")
                    time.sleep(10)  # Berikan waktu agar elemen terlihat

                except Exception as e:
                    print(f"Error clicking the Post button: {e}")
            except Exception as e:
                print(f"Error processing comment at index {idx + 1}: {e}")
    except Exception as e:
        print(f"Error retrieving comments: {e}")
def run_bot():
    """Main bot function to login, process video comments, etc."""
    email = "yiyayuuu"  # Replace with your TikTok email
    password = "FUCKITLIFE1."  # Replace with your TikTok password

    # Initialize driver with mobile emulation
    driver = configure_driver()

    # Load cookies for login
    cookies = load_cookies('tiktok_cookies.pkl')

    # Login to TikTok
    login(driver, email, password, cookies)

    # Process a specific video
    video_url = "https://www.tiktok.com/@yiyayuuu/video/7402587657584315653"
    get_video_and_comment(driver, video_url)


if __name__ == "__main__":
    run_bot()
    
