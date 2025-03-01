import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import get_all_details

test_url = "https://www.vendr.com/marketplace/developer-express"
outpur = get_all_details(test_url)

print(f"found: {outpur}")