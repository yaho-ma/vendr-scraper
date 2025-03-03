def get_bookdetails(page):

    try:
        book_title = page.locator("h1").text_content()
    except Exception as e:
        book_title = f"Locator failed: {str(e)}"

    try:
        category = page.locator("ul.breadcrumb li:nth-child(3) a").text_content()
    except Exception as e:
        category = f"Locator failed: {str(e)}"

    try:
        price = page.locator("p.price_color").first.text_content()
    except Exception as e:
        price = f"Locator failed: {str(e)}"

    try:
        rating_all_text = page.locator("p.star-rating").first.get_attribute("class")
    except Exception as e:
        rating_all_text = f"Locator failed: {str(e)}"

    if rating_all_text:
        rating_last_word = rating_all_text.split()[-1]
    else:
        rating_last_word = "Unknown"

    try:
        book_availability = (
            page.locator("p[class='instock availability']").first.text_content().strip()
        )
    except Exception as e:
        book_availability = f"Locator failed: {str(e)}"

    try:
        image_url_row = page.locator("img").first.get_attribute("src")
    except Exception as e:
        image_url_row = f"Locator failed: {str(e)}"

    image_url = create_full_img_url(image_url_row)

    try:
        description = page.locator("#product_description + p").text_content()
    except Exception as e:
        description = f"Locator failed: {str(e)}"

    try:
        all_product_information = page.locator("table.table.table-striped tr").all()
    except Exception as e:
        all_product_information = f"Locator failed: {str(e)}"

    table_data = {}
    for row in all_product_information:
        th = row.locator("th").text_content().strip()
        td = row.locator("td").text_content().strip()
        table_data[th] = td

    book_details_dict = {
        "book_title": book_title,
        "category": category,
        "price": price,
        "rating": rating_last_word,
        "book_availability": book_availability,
        "image_url": image_url,
        "description": description,
        "product_information": table_data,
    }

    return book_details_dict


def create_full_img_url(str):
    BASE_URL = "https://books.toscrape.com/"

    if not str or "Locator failed" in str:
        return "Image URL not available"

    fist5removed = str[6:]
    full_url = BASE_URL + fist5removed
    return full_url


# write the data to the file


def write_to_file(book_info, filename="books_data.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        file.write("=== Book Details ===\n\n\n")
        for key, value in book_info.items():
            if isinstance(
                value, dict
            ):  # If it's a nested dictionary (product_information)
                file.write(f"{key}:\n")
                for sub_key, sub_value in value.items():
                    file.write(f"  {sub_key}: {sub_value}\n")
            else:
                file.write(f"{key}: {value}\n")
        file.write("\n\n\n")
