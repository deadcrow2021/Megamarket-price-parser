from selenium.webdriver.common.by import By

import traceback
import datetime
import time
import os


def parse_price_str(text: str) -> int:
    list_of_digits = [x for x in text if x.isdigit()]
    number = ''.join(list_of_digits)
    
    return int(number)


def click_price_selector(driver):
    selector_div = driver.find_element(By.CLASS_NAME, 'pdp-tab-selector') # selector with links
    selector_liks = selector_div.find_elements(By.XPATH, '*')

    price_selector = selector_liks[1] # link on Price tab
    price_selector.click()

    time.sleep(0.5)


def catch_error(exception, info = ''):
    message = ''
    error_message = f'{exception} | {traceback.format_exc()}'

    if info:
        message = f'INFO --> {info} <--\n\n'

    message += f'ERROR --> {error_message.rstrip()} <--'

    return message



def fill_log_file(dir_path, text):
    date = datetime.datetime.now()
    
    today = date.strftime('%d_%m_%Y')
    now_time = date.strftime('%H:%M:%S')

    path_to_logs = os.path.join(dir_path, 'logs')
    path_to_file = os.path.join(path_to_logs, f'errors_{today}.log')

    if not os.path.isdir(path_to_logs):
        os.makedirs(path_to_logs, exist_ok=True)

    if os.path.isfile(path_to_file):
        with open(path_to_file, 'a') as file:
            file.write(now_time + ' - ' + text + '\n\n')
    else:
        with open(path_to_file, 'w') as file:
            file.write(now_time + ' - ' + text + '\n\n')
        
    