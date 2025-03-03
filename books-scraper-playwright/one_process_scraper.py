# from playwright.sync_api import sync_playwright, Playwright
# from rich import print
# from utils import get_bookdetails,write_to_file


# def run(playwright: Playwright):
#     start_url = "https://books.toscrape.com/catalogue/page-1.html"
#     chrome = playwright.chromium
#     browser = chrome.launch(headless=False)
#     page = browser.new_page()
#     page.goto(start_url)

#     # тепер знаходимо посилання на всі продукти на 1 сторінці
#     while True:
#         for link in page.locator("a:has(img)").all(): ## знаходить <a> що містить <img>
#             p = browser.new_page(base_url='https://books.toscrape.com/catalogue/') ## відкриваємо нову сторінку браузера
#             url = link.get_attribute('href')
#             if url is not None:
#                 p.goto(url)
#             else:
#                 p.close()


#             #збираємо дані про книгу
#             print("===")
#             book_info = get_bookdetails(p)
#             write_to_file(book_info)
#             print(book_info)
#             print("===")

#             p.close()


#         # check the number of pages
#         page_numbers_list = page.locator("li.current").text_content().split() # this
#         print (f"page_numbers_list: {page_numbers_list}")
#         current_page_num = int(page_numbers_list[1])
#         last_page_num = int(page_numbers_list[-1])

#         if current_page_num == last_page_num:
#             print("Pages have ended")
#             break
#         else:
#             page.locator("a:has-text('next')").click()
#     browser.close()


# with sync_playwright() as playwright:
#     run(playwright)
