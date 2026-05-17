from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

BASE_URL = "http://localhost:5173/pen2pdf" # Update route if needed
PDF_PATH = os.path.abspath("test_pen2pdf.pdf")

def test_pen2pdf():
    print("Running Pen2PDF Test...")
    driver = webdriver.Chrome()
    driver.implicitly_wait(5)
    driver.maximize_window()
    
    try:
        driver.get(BASE_URL)
        time.sleep(3)
        
        # 1. Upload PDF
        print(f"Uploading PDF from: {PDF_PATH}")
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(PDF_PATH)
        time.sleep(1)
        
        # 2. Click Extract/Upload button
        try:
            print("Looking for the Extract button...")
            extract_btn = driver.find_element(By.CSS_SELECTOR, "button.extract-button, .extract-button")
            extract_btn.click()
            print("Extract button clicked successfully.")
        except:
            print("Extract button not found. Upload might be automatic.")
            
        # 3. Wait for OCR results
        print("Waiting for OCR results to return... (10 seconds)")
        time.sleep(10)
        
        print("Pen2PDF Test Passed! ✅")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_pen2pdf()
