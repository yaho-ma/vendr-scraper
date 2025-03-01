import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import get_total_pages

test_url = "https://www.vendr.com/categories/devops/application-development?verified=false&page=1"
pages = get_total_pages(test_url)

print(f"Total pages found: {pages}")
