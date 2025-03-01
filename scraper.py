import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from config import BASE_URL
import urllib.parse
from parser import get_all_details
from database import save_to_db, update_category_in_db


def get_total_pages(category_url):
    
    response = requests.get(category_url)

    if response.status_code != 200:
        print(f"Cannot access {category_url}")
        return 1  # Assume at least one page

    soup = BeautifulSoup(response.text, 'html.parser')

   

    
    spans = soup.find_all('span', class_='rt-Text rt-r-size-2')
    pagination_text = soup.select_one('span.rt-Text.rt-r-size-2')

    for span in spans:
        text = span.text.strip()
        match = re.search(r'Page \d+ of (\d+)', text)
        print(f'the final number is {match}')  
        if match:
            return int(match.group(1))

    return 1 

##################################################################################

def get_first_page_of_every_category():
    
    category_sections = _[
        f"{BASE_URL}/categories/devops",
        f"{BASE_URL}/categories/it-infrastructure",
        f"{BASE_URL}/categories/data-analytics-and-management"
    ]

    first_page_of_category = []

    for section_url in category_sections:

        response = requests.get(section_url)

        if response.status_code != 200:
            print(f"Cannot get the page: {section_url}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')



        for category in soup.find_all('a', class_='rt-Text rt-reset rt-Link rt-r-size-2 rt-underline-auto'):
            category_url = category.get('href')
            if category_url:
                full_url = urljoin(BASE_URL, category_url)
                first_page_of_category.append(full_url)

    return first_page_of_category


#############################################################################################

def get_product_category():
    categories = get_first_page_of_every_category()



    for category_url in categories:
        response = requests.get(category_url)

        if response.status_code != 200:
            print(f"Cannot access {category_url}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        clean_path = urllib.parse.urlparse(category_url).path.split("/")[-1]
        category_name = clean_path.replace("-", " ").title()
        print(category_name)   


        for product in soup.find_all('a', class_='_card_j928a_9 _card_1u7u9_1 _cardLink_1q928_1'): 
            product_url = urljoin(BASE_URL, product.get('href'))

            print(f"from get_product_category: product_url {product_url}")

            # Call get_all_details() to fetch product details
            product_details = get_all_details(product_url)

            print(f"from get_product_category: product_details {product_details}")
            
            
            product_details["category"] = category_name 
            print(f"from get_product_category: NEW CATEGORY {product_details["category"]}")
            product_name = product_details.get("name").strip()

            print("-----------------")
            print(f"Product name: {product_name}")  
            print("-----------------")


            update_category_in_db(product_name, category_name)
    



#############################################################################################

def get_all_pages_for_all_categories():
    
    all_pages = []

    categories = get_first_page_of_every_category()
    for category_url in categories:
        total_pages = get_total_pages(category_url)
        category_pages = [f"{category_url}&page={i}" for i in range(1, total_pages + 1)]
        all_pages.extend(category_pages)

    return all_pages