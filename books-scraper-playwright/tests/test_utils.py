test_str = "../../media/cache/d1/2d/d12d26739b5369a6b5b3024e4d08f907.jpg"


def create_full_img_url(str):
    BASE_URL = "https://books.toscrape.com/"

    fist5removed = str[6:]
    full_url = BASE_URL + fist5removed
    return full_url


to_print = create_full_img_url(test_str)
print(to_print)
