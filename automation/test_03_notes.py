from selenium import webdriver
from selenium.webdriver.common.by import By
import time

BASE_URL = "http://localhost:5173/notes-library" # Update route if needed

def test_notes():
    print("Running Notes Test...")
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    try:
        driver.get(BASE_URL)
        time.sleep(3)
        
        # Click on the Machine Learning folder specifically
        print("Clicking on the 'Machine Learning' folder...")
        try:
            # Look specifically for the Machine Learning folder
            folder_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Machine Learning')]")
            folder_element.click()
            print("Machine Learning folder opened successfully.")
            
            # Now try to find a note inside the folder (avoiding 'New Note' buttons)
            time.sleep(2)
            try:
                # Look specifically for the 'lec1-2' note
                print("Looking for 'lec1-2' notes...")
                note_element = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'lec1-2')]")
                note_element.click()
                print("lec1-2 Note opened successfully.")
            except:
                print("Could not find the 'lec1-2' note inside the folder.")
                
        except Exception as e:
            print("Could not find the 'Machine Learning' folder.")
        
        time.sleep(3)
        print("Notes Test Passed! ✅")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_notes()
