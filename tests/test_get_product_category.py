import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import get_product_category
import urllib.parse


# all_categories = get_product_category()
# print(f'\n {all_categories}')

# for cat in all_categories:
#     print(f"Categories found: {cat}")

test_string="https://www.vendr.com/categories/devops/application-development?verified=false&page=1"

clean_path = urllib.parse.urlparse(test_string).path.split("/")[-1]


category_name = clean_path.replace("-", " ").title()

print(category_name)