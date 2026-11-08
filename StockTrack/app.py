from flask import Flask, render_template, request, redirect, session
from logic.authentication import verify_login
from logic.inventory import (
    load_products, add_product, get_products, search_product, update_product, delete_product, get_low_stock_products, add_restock_request, get_restock_requests, process_restock_request
)

app = Flask(__name__)
app.secret_key = "stocktrack_school_project_key"
load_products()



@app.route("/")
def home():
    if "username" not in session:
        return redirect("/login")

    products = get_products()

    # Total number of products
    total_products = len(products)

    # Total products with stock of 5 or below
    low_stock_count = len(get_low_stock_products())

    # Count unique categories
    total_categories = len({
        product["category"].strip().lower()
        for product in products
    })

    # Get the latest 5 products
    recent_products = list(reversed(products[-5:]))

    return render_template(
        "dashboard.html",
        total_products=total_products,
        low_stock_count=low_stock_count,
        total_categories=total_categories,
        recent_products=recent_products
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if verify_login(username, password):
            session["username"] = username
            return redirect("/")

        return render_template("login.html", error="Invalid username or password.")

    return render_template("login.html")


@app.route("/add-product", methods=["GET", "POST"])
def add_product_page():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        try:
            product = {
                "id": request.form["product_id"].strip(),
                "name": request.form["product_name"].strip(),
                "category": request.form["category"].strip(),
                "quantity": int(request.form["quantity"]),
                "price": float(request.form["price"])
            }

            if not all([
                product["id"],
                product["name"],
                product["category"]
            ]):
                raise ValueError

            if product["quantity"] < 0 or product["price"] < 0:
                raise ValueError

            if add_product(product):
                return render_template(
                    "add_product.html",
                    success="Product successfully added!"
                )

            return render_template(
                "add_product.html",
                error="Product ID already exists."
            )

        except ValueError:
            return render_template(
                "add_product.html",
                error="Please enter valid product information."
            )

    return render_template("add_product.html")


@app.route("/inventory")
def view_inventory():
    if "username" not in session:
        return redirect("/login")

    products = get_products()

    return render_template(
        "inventory.html",
        products=products
    )


@app.route("/search-product", methods=["GET", "POST"])
def search_product_page():
    if "username" not in session:
        return redirect("/login")

    results = []
    searched = False
    keyword = ""

    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        searched = True

        if keyword:
            results = search_product(keyword)

    return render_template(
        "search_product.html",
        results=results,
        searched=searched,
        keyword=keyword
    )




@app.route("/update-stock", methods=["GET", "POST"])
def update_stock_page():
    if "username" not in session:
        return redirect("/login")

    message = None
    error = None
    selected_product_id = ""

    products = get_products()

    if request.method == "POST":
        product_id = request.form.get("product_id", "").strip()
        quantity_input = request.form.get("quantity", "").strip()
        remarks = request.form.get("remarks", "").strip()

        selected_product_id = product_id

        try:
            if not product_id:
                raise ValueError

            new_quantity = int(quantity_input)

            if new_quantity < 0:
                raise ValueError

            if update_product(product_id, new_quantity):
                message = "Stock successfully updated!"

                # Refresh product list after updating
                products = get_products()

            else:
                error = "Product ID not found."

        except ValueError:
            error = "Please enter a valid Product ID and quantity."

    return render_template(
        "update_stock.html",
        products=products,
        message=message,
        error=error,
        selected_product_id=selected_product_id
    )


@app.route("/delete-product", methods=["GET", "POST"])
def delete_product_page():
    if "username" not in session:
        return redirect("/login")

    message = None
    error = None

    if request.method == "POST":
        product_id = request.form.get("product_id", "").strip()

        if not product_id:
            error = "Please enter a Product ID."
        elif delete_product(product_id):
            message = "Product successfully deleted!"
        else:
            error = "Product ID not found."

    return render_template(
        "delete_product.html",
        message=message,
        error=error,
        products=get_products()
    )


@app.route("/low-stock")
def low_stock_page():
    if "username" not in session:
        return redirect("/login")

    threshold_input = request.args.get("threshold", "5")

    try:
        threshold = int(threshold_input)

        if threshold < 0:
            threshold = 5

    except ValueError:
        threshold = 5

    products = get_low_stock_products(threshold)

    return render_template(
        "low_stock.html",
        products=products,
        threshold=threshold
    )

@app.route("/restock-requests", methods=["GET", "POST"])
def restock_requests_page():
    if "username" not in session:
        return redirect("/login")

    message = None
    error = None

    if request.method == "POST":
        product_id = request.form.get("product_id", "").strip()
        quantity_input = request.form.get("quantity", "").strip()

        try:
            if not product_id:
                raise ValueError

            quantity = int(quantity_input)

            if quantity <= 0:
                raise ValueError

            # Check if Product ID exists
            product_exists = any(
                product["id"].lower() == product_id.lower()
                for product in get_products()
            )

            if not product_exists:
                error = "Product ID not found."
            else:
                add_restock_request(product_id, quantity)
                message = "Restock request successfully added!"

        except ValueError:
            error = "Please enter a valid Product ID and quantity."

    return render_template(
        "restock_requests.html",
        products=get_products(),
        restock_requests=get_restock_requests(),
        message=message,
        error=error
    )

@app.route("/process-restock-request", methods=["POST"])
def process_restock_page():
    if "username" not in session:
        return redirect("/login")

    processed = process_restock_request()

    if processed is None:
        return redirect("/restock-requests")

    return redirect("/restock-requests")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)