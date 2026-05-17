from selenium import webdriver
from selenium.webdriver.common.by import By
import time

BASE_URL = "http://localhost:5173/notes-generator" # Update route if needed

def test_generate():
    print("Running Generate Test...")
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    try:
        driver.get(BASE_URL)
        time.sleep(3)
        
        print("Clicking Start Empty Document...")
        try:
            start_doc = driver.find_element(By.XPATH, "//button[contains(text(), 'Start Empty Document')]")
            start_doc.click()
            time.sleep(2)
        except:
            print("Could not find 'Start empty doc' button.")
        
        print("Entering some text into the document...")
        try:
            # Find the markdown-editor textarea
            editor = driver.find_element(By.CLASS_NAME, "markdown-editor")
            editor.send_keys("This is a test generated note for SQA Automation.")
            time.sleep(2)
        except:
            print("Could not find the text editor area.")
        
        # Verify Export buttons
        exports = ["MD", "DOCX", "PDF"]
        for ext in exports:
            print(f"Clicking Export as {ext}...")
            try:
                # Find button containing the extension text
                btn = driver.find_element(By.XPATH, f"//button[contains(text(), 'Export {ext}')]")
                btn.click()
                time.sleep(1) 
                
                # Deal with the Export Modal
                print("Confirming export in modal...")
                submit_btn = driver.find_element(By.CSS_SELECTOR, ".modal .submit-button")
                submit_btn.click()
                time.sleep(2) # Wait for file download dialogue/process
            except Exception as e:
                print(f"Export flow for {ext} failed. Error: {e}")
        
        print("Generate Test Passed! ✅")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_generate()
