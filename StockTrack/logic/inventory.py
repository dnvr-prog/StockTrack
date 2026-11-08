import json
import os
from collections import deque

# Product storage file
DATA_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "products.json"
)

# List data structure
products = []

# Queue Data Structure (FIFO)
restock_queue = deque()


def load_products():
    global products

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            products = json.load(file)
    else:
        products = []

    return products


def save_products():
    with open(DATA_FILE, "w") as file:
        json.dump(products, file, indent=4)


def add_product(product):
    for item in products:
        if item["id"].lower() == product["id"].lower():
            return False

    products.append(product)
    save_products()
    return True


def get_products():
    return products


def search_product(keyword):
    keyword = keyword.strip().lower()

    results = []

    for product in products:
        if (keyword in product["id"].lower()
                or keyword in product["name"].lower()):
            results.append(product)

    return results


def update_product(product_id, new_quantity):
    for product in products:
        if product["id"].lower() == product_id.lower():
            product["quantity"] = new_quantity
            save_products()
            return True

    return False

def delete_product(product_id):
    for product in products:
        if product["id"].lower() == product_id.lower():
            products.remove(product)
            save_products()
            return True

    return False

def get_low_stock_products(threshold=5):
    low_stock = []

    for product in products:
        if product["quantity"] <= threshold:
            low_stock.append(product)

    return low_stock

# Add a restock request to the Queue
def add_restock_request(product_id, quantity):
    request = {
        "product_id": product_id,
        "quantity": quantity
    }

    restock_queue.append(request)
    return True


# Get all pending restock requests
def get_restock_requests():
    return list(restock_queue)


# Process the first request in the Queue
def process_restock_request():
    if not restock_queue:
        return None

    request = restock_queue.popleft()

    for product in products:
        if product["id"].lower() == request["product_id"].lower():
            product["quantity"] += request["quantity"]
            save_products()
            return request

    return request