from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from bot import bot

import pandas as pd
import time

from custom_functions import (
    parse_price_str,
    click_price_selector,
    catch_error,
    fill_log_file
)

from constants import (
    CHAT_ID,
    DELAY_BETWEEN_LINKS,
    DELAY_BETWEEN_PARSE_CYCLES,
    DATA_PATH,
    PRICE_SHOPS,
    BONUS_SHOPS
)


app = FastAPI()

options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(1600, 900)


data = pd.read_excel(DATA_PATH)

links = data['Ссылка']
titles = data['Наименование']


@app.on_event("startup")
@repeat_every(seconds = 60 * DELAY_BETWEEN_PARSE_CYCLES)
async def parse_links() -> None:
    messages_list_to_send = []
    messages_heap = []

    for ind in range(data.shape[0]):
        price_shops_details = {}
        bonus_shops_details = {}
        other_shops = {}

        link = links[ind]
        title = titles[ind]
        
        try:

            print(f'Обработка ссылки № {ind + 1}:  -  ', link, title)
            
            slash = '' if link.endswith('/') else '/'
            
            try:
                driver.get(link + slash + '#?details_block=prices')
                time.sleep(2)
            except:
                try:
                    driver.get(link)
                    time.sleep(2)
                    click_price_selector(driver)

                except:
                    try:
                        driver.find_element(By.CLASS_NAME, 'not-found')
                        info = f'INFO - Ссылка № {ind + 1} - {link}, возможно, не существует.'
                        messages_list_to_send.append(info)
                        continue
                    except Exception as exc:
                        fill_log_file(catch_error(exc))
                        continue

            try:
                cards_list_div = driver.find_element(By.CLASS_NAME, 'product-offers') # prices list div
                cards_list = cards_list_div.find_elements(By.CLASS_NAME, 'product-offer')

            except Exception as exc:
                info = f'Ссылка № {ind + 1} - {link}, возможно, не содержит вкладку "Цена".'
                fill_log_file(catch_error(exc, info))


            for card in cards_list:
                
                try:
                    shop_name_block = card.find_element(By.CLASS_NAME, 'pdp-merchant-rating-block__merchant-name')
                    shop_name = shop_name_block.text
                except Exception as e:
                    shop_name = 'Undefined'

                try:
                    delivery_type_div = card.find_element(By.CLASS_NAME, 'offer-item-delivery-type')
                    delivery_type_child_elements = delivery_type_div.find_elements(By.XPATH, '*')
                    delivery_type = delivery_type_child_elements[0].text # доставка по клику / курьером
                except Exception as e:
                    delivery_type = ''

                try:
                    price_div = card.find_element(By.CLASS_NAME, 'product-offer-price__amount')
                    price = parse_price_str(price_div.text)
                except Exception as e:
                    price = 0

                try:
                    bonuses_div = card.find_element(By.CLASS_NAME, 'product-offer-price-bonus')
                    bonuses_text = bonuses_div.find_element(By.CLASS_NAME, 'bonus-amount')
                    bonus = parse_price_str(bonuses_text.text)
                except Exception as exc:
                    bonus = 0

                card_data = {
                        'price': price,
                        'bonus': bonus,
                    }
                
                # print(shop_name, delivery_type, price, bonus)

                if shop_name in PRICE_SHOPS:
                    price_shops_details[shop_name] = card_data

                elif shop_name in BONUS_SHOPS:
                    bonus_shops_details[shop_name] = card_data

                else:
                    if 'клик' in delivery_type:
                        other_shops[shop_name] = card_data
                
            # print(price_shops_details, bonus_shops_details, other_shops)
        
        except Exception as exc:
            fill_log_file(catch_error(exc))
            price_shops_details, bonus_shops_details, other_shops = {}, {}, {}
            


        try:
            message = ''
            bonus_shops_message = ''
            better_offers_shops = []
            our_best_offer = None

            if price_shops_details:
                # 1 - check only price
                if any(price_shops_details[s]['price'] for s in price_shops_details):
                    our_max_price = max([price_shops_details[s]['price'] for s in price_shops_details])
                    lowest_price = our_max_price
                    lowest_price_shop = None
                    
                    price_shops_message = [
                        f'{s} - Цена: {price_shops_details[s]["price"]}' +
                            f' | Бонусы: {price_shops_details[s]["bonus"]}' if price_shops_details[s]["bonus"] else ''
                        for s in price_shops_details
                        ]
                else:
                    print('Ни у одного из наших магазинов не указана цена. Либо произошла неизвестная ошибка.')
                    # continue

            if bonus_shops_details:
                # 2 - check bonuses
                if any(bonus_shops_details[s]['price'] for s in bonus_shops_details):
                    
                    for s in bonus_shops_details:
                        if our_best_offer and (bonus_shops_details[s]['price'] - bonus_shops_details[s]['bonus'] < our_best_offer['price'] - our_best_offer['bonus']):
                            our_best_offer = {
                                            'name': s,
                                            'price': bonus_shops_details[s]['price'],
                                            'bonus': bonus_shops_details[s]['bonus'],
                                            }
                        else:
                            our_best_offer = {
                                            'name': s,
                                            'price': bonus_shops_details[s]['price'],
                                            'bonus': bonus_shops_details[s]['bonus'],
                                            }
                    
                    bonus_shops_message = [
                        f'{s} - Цена: {bonus_shops_details[s]["price"]}' +
                            f' | Бонусы: {bonus_shops_details[s]["bonus"]}' if bonus_shops_details[s]["bonus"] else ''
                        for s in bonus_shops_details
                        ]
                else:
                    print('Ни у одного из наших магазинов не указана цена. Либо произошла неизвестная ошибка.')
            
            if not price_shops_details and not bonus_shops_details:
                continue


            for shop in other_shops:
                shop_price = other_shops[shop]['price']
                shop_bonus = other_shops[shop]['bonus']

                if price_shops_details:
                    if shop_price < lowest_price:
                        lowest_price = shop_price
                        lowest_price_shop = {
                                            'name': shop,
                                            'price': shop_price,
                                            'bonus': shop_bonus,
                                            }
                
                if bonus_shops_details:
                    diff = shop_price - shop_bonus
                    our_diff = our_best_offer['price'] - our_best_offer['bonus']
                
                    if diff < our_diff:
                        better_offers_shops.append(
                            {
                            'name': shop,
                            'price': shop_price,
                            'bonus': shop_bonus,
                            }
                        )

            if lowest_price_shop and price_shops_details:
                price_record = f'{lowest_price_shop["name"]} - Цена: {lowest_price_shop["price"]}' + \
                                f' | Бонусы: {lowest_price_shop["bonus"]}' if lowest_price_shop["bonus"] else ''

                message += 'Обнаружена более выгодная цена.\nНаши предложения:\n' + '\n'.join(price_shops_message) + '\n\n'
                message += f'Лучшее предложение: {price_record}' + '\n\n\n'


            if bonus_shops_details and better_offers_shops:
                bonus_records = [
                        f'{s["name"]} - Цена: {s["price"]}' +
                            f' | Бонусы: {s["bonus"]}' if s["bonus"] else ''
                        for s in better_offers_shops
                        ]

                message += 'Обнаружена более выгодная цена с бонусами.\nНаши предложения:\n' + '\n'.join(bonus_shops_message) + '\n\n'
                message += f'Лучшие предложения:\n' + '\n'.join(bonus_records) + '\n\n'
            
            if message:
                message = f'Ссылка № {ind + 1}: - {link} | Название: {title}\n\n' + message
                message = message.rstrip()
                message += '\n\n=============================\n'
                messages_heap.append(message)

        except Exception as exc:
            fill_log_file(catch_error(exc))
        
        joined_messages_heap = '\n\n'.join(messages_heap)

        if len(joined_messages_heap) > 3000:
            messages_list_to_send.append(joined_messages_heap)
            messages_heap = []

        time.sleep(DELAY_BETWEEN_LINKS)


    if messages_heap and joined_messages_heap:
        messages_list_to_send.append(joined_messages_heap)

    for msg in messages_list_to_send:
        await bot.send_message(CHAT_ID, msg)

    print('finish cycle')
