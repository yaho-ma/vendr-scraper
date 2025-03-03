from playwright.sync_api import sync_playwright
import signal
import queue
import os
from rich import print
from process_manager import ProcessManager


def get_bookdetails(page):
    title = page.locator("h1").inner_text()
    price = page.locator(".price_color").inner_text()
    availability = page.locator(".availability").inner_text().strip()
    try:
        rating = page.locator(".star-rating").get_attribute("class").split()[-1]
    except:
        rating = "No rating"

    return {
        "book_title": title,
        "price": price,
        "availability": availability,
        "rating": rating,
        "url": page.url,
    }


def create_full_img_url(relative_url):
    return "https://books.toscrape.com/" + relative_url.replace("../", "")


def write_to_file(book_data):
    # Create the directory if it doesn't exist
    os.makedirs("books_data", exist_ok=True)

    # Create or append to the file
    with open("books_data/books.txt", "a", encoding="utf-8") as f:
        f.write(f"Title: {book_data['book_title']}\n")
        f.write(f"Price: {book_data['price']}\n")
        f.write(f"Availability: {book_data['availability']}\n")
        f.write(f"Rating: {book_data['rating']}\n")
        f.write(f"URL: {book_data['url']}\n")
        f.write("-" * 50 + "\n")

    print(f"Wrote data for book: {book_data['book_title']}")


try:
    from utils import get_bookdetails, create_full_img_url, write_to_file
except ImportError:
    print("Using built-in utility functions as utils.py was not found")


def worker_process(worker_id, task_queue, results_queue, stop_event):
    """Worker process that handles scraping"""
    print(f"Worker {worker_id} starting")

    # Set up signal handler for shutdown
    def handle_signal(signum, frame):
        print(f"Worker {worker_id} received signal {signum}")
        stop_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Each process launches its own browser
    try:
        with sync_playwright() as playwright:
            chrome = playwright.chromium
            browser = chrome.launch(headless=True)  # Change to False for testing

            while not stop_event.is_set():
                try:
                    # Try to get a task with timeout
                    try:
                        url = task_queue.get(timeout=5)
                    except queue.Empty:
                        # No more tasks, check if you can stop
                        if stop_event.is_set():
                            break
                        continue

                    # Process the page
                    process_page(worker_id, browser, url, results_queue)

                    # Signal that task is complete
                    results_queue.put("COMPLETED_TASK")

                except Exception as e:
                    print(f"Worker {worker_id} encountered error: {str(e)}")
                    # Continue with next task

            # close the browser
            browser.close()
            print(f"Worker {worker_id} shutting down")

    except Exception as e:
        print(f"Worker {worker_id} failed to initialize: {str(e)}")


def process_page(worker_id, browser, url, results_queue):
    """Process a single page of book listings"""
    print(f"Worker {worker_id} processing page: {url}")

    # Create a new page for the catalog page
    page = browser.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Find all book links on the page
        book_links = page.locator("h3 > a").all()
        book_urls = [link.get_attribute("href") for link in book_links]

        # Process each book
        for book_url in book_urls:
            if book_url:
                # Make sure we have the correct book URL
                if book_url.startswith("http"):
                    full_url = book_url
                else:
                    # Handle relative URLs by constructing absolute URL
                    if book_url.startswith("/"):
                        full_url = f"https://books.toscrape.com{book_url}"
                    else:
                        full_url = f"https://books.toscrape.com/catalogue/{book_url}"

                book_page = browser.new_page()
                try:
                    book_page.goto(
                        full_url, wait_until="domcontentloaded", timeout=30000
                    )
                    book_info = get_bookdetails(book_page)

                    # Send book data to main process
                    results_queue.put("BOOK_DATA")
                    results_queue.put(book_info)

                    print(f"Worker {worker_id} scraped: {book_info['book_title']}")
                except Exception as e:
                    print(
                        f"Worker {worker_id} error processing book {full_url}: {str(e)}"
                    )
                finally:
                    book_page.close()

        # Check if there are more pages to process
        try:
            # Using a more reliable way to find next button
            has_next = page.locator("ul.pager li.next").count() > 0

            if has_next:
                next_url = page.locator("ul.pager li.next a").get_attribute("href")
                if next_url:
                    # Construct absolute URL properly based on current URL
                    if next_url.startswith("http"):
                        next_full_url = next_url
                    else:
                        # Make sure we handle the URL correctly
                        if "/" in url:
                            base_url = url.rsplit("/", 1)[0] + "/"
                        else:
                            base_url = url + "/"

                        next_full_url = f"{base_url}{next_url}"

                    # Debug print
                    print(f"Worker {worker_id} FOUND NEXT PAGE: {next_full_url}")

                    # Add the new page to the task queue
                    results_queue.put("FOUND_NEW_PAGE")
                    results_queue.put(next_full_url)
                    print(
                        f"Worker {worker_id} added next page to queue: {next_full_url}"
                    )
                else:
                    print(f"Worker {worker_id} found next button but couldn't get URL")
            else:
                print(f"Worker {worker_id} no next page found on {url}")

                # Debug the pager
                pager_html = page.locator("ul.pager").inner_html()
                print(f"Pager HTML: {pager_html}")

        except Exception as e:
            print(f"Worker {worker_id} error finding next page: {str(e)}")
            import traceback

            traceback.print_exc()

    except Exception as e:
        print(f"Worker {worker_id} error processing catalog page {url}: {str(e)}")
    finally:
        page.close()


def handle_book_data(book_data):
    write_to_file(book_data)


# This is the main function that runs the scraper
def main():
    print("Book scraper starting...")
    start_url = "https://books.toscrape.com/catalogue/page-1.html"

    # Create and start the process manager with 3 processes
    manager = ProcessManager(num_processes=3)
    manager.set_worker_function(worker_process)
    manager.set_book_data_handler(handle_book_data)

    try:
        manager.start(start_url, worker_process)
        print("Scraper completed successfully")
    except Exception as e:
        print(f"Scraper failed with error: {str(e)}")


if __name__ == "__main__":
    # This ensures the code only runs when executed directly
    # It prevents execution when imported as a module
    main()
