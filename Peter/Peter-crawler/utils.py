from selenium.webdriver.common.by import By
import time

def scroll_to_bottom(driver):
    """滑到 Google Maps 搜尋結果的最底部"""
    scrollable_div_xpath = '//div[contains(@aria-label, "搜尋結果")]'
    scrollable = driver.find_element(By.XPATH, scrollable_div_xpath)
    
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable)
    same_count = 0

    while same_count < 3:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
        time.sleep(2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable)

        if new_height == last_height:
            same_count += 1
        else:
            same_count = 0
            last_height = new_height
