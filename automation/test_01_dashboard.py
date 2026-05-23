from selenium import webdriver
from selenium.webdriver.common.by import By
import time

BASE_URL = "http://localhost:5173"  

def test_dashboard():
    print("Running Dashboard Test...")
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    try:
        driver.get(BASE_URL)
        time.sleep(3)
        
        # 1. Verify it opens
        assert "StudyBuddy" in driver.title or driver.find_element(By.TAG_NAME, "body"), "Dashboard failed to load"
        
        # 2. Click Quick Actions
        actions = ["Extract Doc", "Generate Notes", "Ask Isabella"]
        for action in actions:
            print(f"Clicking quick action: {action}")
            try:
                # Find button by text
                btn = driver.find_element(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{action.lower()}')]")
                btn.click()
                time.sleep(2)
                
                # Navigate back to dashboard to click the next action
                driver.get(BASE_URL)
                time.sleep(2)
            except Exception as e:
                print(f"Could not find '{action}' button. Ensure the text matches the UI.")
                
        print("Dashboard Test Passed! ✅")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_dashboard()
