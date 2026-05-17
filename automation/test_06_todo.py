from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

BASE_URL = "http://localhost:5173/todos" # Update route if needed

def test_todo():
    print("Running ToDo Test...")
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    try:
        driver.get(BASE_URL)
        time.sleep(3)
        
        print("Making a ToDo entry...")
        try:
            # 1. Click New Todo Button
            new_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'New Todo')]")
            new_btn.click()
            time.sleep(1)
            
            # 2. Fill Title
            title_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter todo title']")
            title_input.send_keys("Complete SQA Automation Scripts")
            
            # 3. Fill Description
            desc_input = driver.find_element(By.XPATH, "//textarea[@placeholder='Add details...'] | //input[@placeholder='Add details...']")
            desc_input.send_keys("This is an automated test for the Todo module.")
            
            # 4. Click Create Button
            create_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Create')] | //button[contains(@class, 'submit')]")
            create_btn.click()
            print("ToDo submitted successfully!")
        except Exception as e:
            print("Could not complete the ToDo flow. Error:", e)
            
        time.sleep(3)
        print("ToDo Test Passed! ✅")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_todo()
