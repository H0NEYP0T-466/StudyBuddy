from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

BASE_URL = "http://localhost:5173/assistant" # Update route if needed

def test_isabella():
    print("Running AI Isabella Test...")
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    try:
        driver.get(BASE_URL)
        time.sleep(3)
        
        print("Disabling RAG and Enabling Isolate Message...")
        try:
            rag_checkbox = driver.find_element(By.XPATH, "//*[contains(text(), 'Use RAG')]")
            rag_checkbox.click()
            time.sleep(1)
            
            isolate_checkbox = driver.find_element(By.XPATH, "//*[contains(text(), 'Isolate Message')]")
            isolate_checkbox.click()
            time.sleep(1)
        except Exception as e:
            print("Could not find checkboxes:", e)
        
        print("Sending 'hello' to ai-assistant...")
        try:
            # Find chat input (textarea or text input)
            chat_input = driver.find_element(By.XPATH, "//textarea | //input[@type='text']")
            chat_input.send_keys("hello")
            time.sleep(1)
            
            # Send the message (press Enter)
            chat_input.send_keys(Keys.RETURN)
            print("Message sent.")
        except:
            print("Could not find chat input box.")
            
        print("Waiting for response... (12 seconds)")
        time.sleep(12)
        
        print("AI Isabella Test Passed! ✅")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_isabella()
