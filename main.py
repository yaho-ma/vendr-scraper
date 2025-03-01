import threading
import queue
from scraper import get_all_pages_for_all_categories
from parser import get_all_individual_pages, get_all_details
from database import create_table, save_to_db
from scraper import get_product_category

task_queue = queue.Queue()
NUM_WORKERS = 5  # Кількість потоків для парсингу


def update_product_categories():
    print("Оновлення категорій продуктів у базі...")
    get_product_category()
    print("Категорії оновлено!")


def worker():
    while True:
        product_url = task_queue.get()
        if product_url is None:
            break  
        
        product_details = get_all_details(product_url)
        if product_details:
            save_to_db(product_details)
        task_queue.task_done()

def main():
    create_table()

    print("Збираємо всі сторінки категорій...")
    category_pages = get_all_pages_for_all_categories()

    print("Збираємо всі продукти...")
    for category_page in category_pages:
        product_links = get_all_individual_pages(category_page)
        for product_url in product_links:
            task_queue.put(product_url)

    
    threads = []
    for _ in range(NUM_WORKERS):
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    task_queue.join()

    
    for _ in range(NUM_WORKERS):
        task_queue.put(None)
    for thread in threads:
        thread.join()

    print("Завершено!")

if __name__ == "__main__":
    main()
    #update_product_categories()