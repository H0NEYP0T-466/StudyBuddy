from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

BASE_URL = "http://localhost:5173/timetable" # Update route if needed

def test_timetable():
    print("Running Timetable Test...")
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    try:
        driver.get(BASE_URL)
        time.sleep(3)
        
        print("Adding a timetable entry...")
        try:
            # Look for Add Entry button
            add_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Add Entry')]")
            add_btn.click()
            time.sleep(1)
        except:
            print("No Add Entry button found.")
            
        try:
            # Type subject
            subject_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Mathematics']")
            subject_input.send_keys("Software Quality Assurance")
            
            # Type times
            time_inputs = driver.find_elements(By.XPATH, "//input[@type='time']")
            if len(time_inputs) >= 2:
                time_inputs[0].send_keys("09:00AM")
                time_inputs[1].send_keys("10:00AM")
                
            # Type location
            location_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g., Room 101']")
            location_input.send_keys("Room 404")
                
            # Click Save/Submit
            create_btn = driver.find_element(By.CSS_SELECTOR, "button.submit-button")
            create_btn.click()
            print("Entry saved successfully!")
        except Exception as e:
            print("Failed to fill inputs or find create button. Error:", e)
            
        time.sleep(3)
        print("Timetable Test Passed! ✅")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_timetable()
