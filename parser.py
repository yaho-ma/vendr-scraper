import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import BASE_URL

def get_all_individual_pages(url_with_page):

    response = requests.get(url_with_page)

    if response.status_code != 200:
        print(f"Cannot access {url_with_page}")
        return None
    
    
    soup = BeautifulSoup(response.text, 'html.parser')
    individual_link = soup.find_all('a', class_='_card_j928a_9 _card_1u7u9_1 _cardLink_1q928_1')

    list_of_links = []

    for link in individual_link:
        link = link.get('href')
        full_link = urljoin(BASE_URL, link)
        list_of_links.append(full_link)
        
    return list_of_links


###################

def get_all_details(individual_page):
    
    response = requests.get(individual_page)

    if response.status_code != 200:
        print(f"Cannot access {individual_page}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        name = soup.find('h1', class_='rt-Heading rt-r-size-6 xs:rt-r-size-8').text.strip()
    except AttributeError:
        name = "N/A"

    try:
        category = soup.find('h1', class_='rt-Heading rt-r-size-6 xs:rt-r-size-8').text.strip()
    except AttributeError:
        category = "N/A"

    try:
        description = soup.find('p', class_='rt-Text').text.strip()
    except AttributeError:
        description = "N/A"

    try:
        price_low = soup.find('span', class_='v-fw-600 v-fs-12').text.strip()
    except AttributeError:
        price_low = "N/A"
        

    try:
        price_median = soup.find('span', class_='v-fw-700 v-fs-24').text.strip()
    except AttributeError:
        price_median = "N/A"    

    try:
        price_high = soup.find('span', class_='_rangeSliderLastNumber_118fo_38 v-fw-600 v-fs-12').text.strip()
    except AttributeError:
        price_high = "N/A"

    return {
        "name": name,
        "category": category,
        "price_low": price_low,
        "price_median": price_median,
        "price_high": price_high,
        "description": description,
        }