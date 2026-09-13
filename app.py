from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)

# Secret Key
app.config["SECRET_KEY"] = config.SECRET_KEY


# =========================
# MySQL Connection Function
# =========================


def get_db_connection():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
    )


# =========================
# Home / Login Page
# =========================


@app.route("/")
def home():
    return render_template("login.html")


# =========================
# Signup Page
# =========================


@app.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")


# =========================
# Signup
# =========================


@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    fullname = data["fullname"]
    username = data["username"]
    email = data["email"]
    phone = data["phone"]
    password = data["password"]

    # Hash Password
    password = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (fullname, username, email, phone, password)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (fullname, username, email, phone, password),
        )

        db.commit()

        return jsonify({"success": True, "message": "Account created successfully."})

    except mysql.connector.IntegrityError:

        db.rollback()

        return (
            jsonify({"success": False, "message": "Username or email already exists."}),
            409,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Login Page
# =========================


@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


# =========================
# Login
# =========================


@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data["username"]
    password = data["password"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT * FROM users
            WHERE username = %s OR email = %s
            """,
            (username, username),
        )

        user = cursor.fetchone()

        if user:

            if check_password_hash(user["password"], password):

                # Create Session
                session["user_id"] = user["id"]
                session["username"] = user["username"]

                return jsonify({"success": True, "message": "Login successful."})

        return (
            jsonify(
                {"success": False, "message": "Invalid username/email or password."}
            ),
            401,
        )

    except mysql.connector.Error as error:

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Dashboard
# =========================


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("dashboard.html", full_name=full_name)


# =========================
# Logout
# =========================


@app.route("/logout")
def logout():

    # Remove all session data
    session.clear()

    # Redirect to login page
    return redirect(url_for("home"))


# ===============================
# DASHBOARD STATS
# ===============================


@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        # ===============================
        # TOTAL PRODUCTS
        # ===============================

        cursor.execute("""
            SELECT COUNT(*) AS total_products
            FROM products
            """)

        total_products = cursor.fetchone()["total_products"]

        # ===============================
        # TOTAL CATEGORIES
        # ===============================

        cursor.execute("""
            SELECT COUNT(*) AS total_categories
            FROM categories
            """)

        total_categories = cursor.fetchone()["total_categories"]

        # ===============================
        # TOTAL CUSTOMERS
        # ===============================

        cursor.execute("""
            SELECT COUNT(*) AS total_customers
            FROM customers
            """)

        total_customers = cursor.fetchone()["total_customers"]

        # ===============================
        # LOW STOCK PRODUCTS
        # ===============================

        cursor.execute("""
            SELECT COUNT(*) AS low_stock
            FROM products
            WHERE stock_quantity <= minimum_stock
            """)

        low_stock = cursor.fetchone()["low_stock"]

        # ===============================
        # TODAY'S SALES
        # ===============================

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(final_amount),
                    0
                ) AS today_sales

            FROM sales

            WHERE DATE(created_at) = CURDATE()
            """)

        today_sales = cursor.fetchone()["today_sales"]

        # ===============================
        # RECENT SALES
        # ===============================

        cursor.execute("""
            SELECT
                s.id AS invoice,

                COALESCE(
                    c.customer_name,
                    'Walk-in Customer'
                ) AS customer,

                DATE_FORMAT(
                    s.created_at,
                    '%d %b %Y'
                ) AS date,

                s.final_amount AS amount,

                'Completed' AS status

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.id

            ORDER BY s.created_at DESC

            LIMIT 5
            """)

        recent_sales = cursor.fetchall()

        # ===============================
        # LOW STOCK PRODUCTS LIST
        # ===============================

        cursor.execute("""
            SELECT
                product_name AS name,
                stock_quantity AS quantity

            FROM products

            WHERE stock_quantity <= minimum_stock

            ORDER BY stock_quantity ASC

            LIMIT 5
            """)

        low_stock_products = cursor.fetchall()

        # ===============================
        # RESPONSE
        # ===============================

        return (
            jsonify(
                {
                    "success": True,
                    "total_products": total_products,
                    "total_categories": total_categories,
                    "total_customers": total_customers,
                    "low_stock": low_stock,
                    "today_sales": float(today_sales or 0),
                    "recent_sales": recent_sales,
                    "low_stock_products": low_stock_products,
                }
            ),
            200,
        )

    except mysql.connector.Error as error:

        print("Dashboard stats database error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database error while loading dashboard stats.",
                }
            ),
            500,
        )

    except Exception as error:

        print("Dashboard stats error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while loading dashboard stats.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================
# Categories Page
# =========================


@app.route("/categories")
def categories():
    return render_template("categories.html")


# =========================
# Get All Categories
# =========================


@app.route("/api/categories", methods=["GET"])
def get_categories():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id,
                name,
                description,
                status,
                created_at,
                updated_at
            FROM categories
            ORDER BY id DESC
        """)

        categories = cursor.fetchall()

        return jsonify({"success": True, "categories": categories}), 200

    except mysql.connector.Error as error:

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Get One Category
# =========================


@app.route("/api/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute(
            """
            SELECT
                id,
                name,
                description,
                status,
                created_at,
                updated_at
            FROM categories
            WHERE id = %s
            """,
            (category_id,),
        )

        category = cursor.fetchone()

        if not category:

            return jsonify({"success": False, "message": "Category not found."}), 404

        return jsonify({"success": True, "category": category}), 200

    except mysql.connector.Error as error:

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Create Category
# =========================


@app.route("/api/categories", methods=["POST"])
def create_category():

    data = request.get_json()

    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    status = data.get("status", "active")

    if not name:

        return jsonify({"success": False, "message": "Category name is required."}), 400

    db = get_db_connection()
    cursor = db.cursor()

    try:

        # Check duplicate category
        cursor.execute(
            """
            SELECT id
            FROM categories
            WHERE LOWER(name) = LOWER(%s)
            """,
            (name,),
        )

        existing_category = cursor.fetchone()

        if existing_category:

            return (
                jsonify({"success": False, "message": "Category already exists."}),
                409,
            )

        cursor.execute(
            """
            INSERT INTO categories
                (name, description, status)
            VALUES
                (%s, %s, %s)
            """,
            (name, description, status),
        )

        db.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Category created successfully.",
                    "category_id": cursor.lastrowid,
                }
            ),
            201,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Update Category
# =========================


@app.route("/api/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):

    data = request.get_json()

    name = data.get("name", "").strip()
    description = data.get("description", "").strip()
    status = data.get("status", "active")

    if not name:

        return jsonify({"success": False, "message": "Category name is required."}), 400

    db = get_db_connection()
    cursor = db.cursor()

    try:

        # Check whether category exists
        cursor.execute(
            """
            SELECT id
            FROM categories
            WHERE id = %s
            """,
            (category_id,),
        )

        category = cursor.fetchone()

        if not category:

            return jsonify({"success": False, "message": "Category not found."}), 404

        # Check duplicate name
        cursor.execute(
            """
            SELECT id
            FROM categories
            WHERE LOWER(name) = LOWER(%s)
            AND id != %s
            """,
            (name, category_id),
        )

        duplicate = cursor.fetchone()

        if duplicate:

            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Another category with this name already exists.",
                    }
                ),
                409,
            )

        cursor.execute(
            """
            UPDATE categories
            SET
                name = %s,
                description = %s,
                status = %s
            WHERE id = %s
            """,
            (name, description, status, category_id),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Category updated successfully."}),
            200,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Delete Category
# =========================


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):

    db = get_db_connection()
    cursor = db.cursor()

    try:

        # Check whether category exists
        cursor.execute(
            """
            SELECT id
            FROM categories
            WHERE id = %s
            """,
            (category_id,),
        )

        category = cursor.fetchone()

        if not category:

            return jsonify({"success": False, "message": "Category not found."}), 404

        cursor.execute(
            """
            DELETE FROM categories
            WHERE id = %s
            """,
            (category_id,),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Category deleted successfully."}),
            200,
        )

    except mysql.connector.IntegrityError:

        db.rollback()

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Category cannot be deleted because it is being used by a product.",
                }
            ),
            409,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Products Page
# =========================


@app.route("/products")
def products():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("products.html", full_name=full_name)


# =========================
# Get All Products
# =========================


@app.route("/api/products", methods=["GET"])
def get_products():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            products.id,
            products.product_name,
            products.sku,
            products.category_id,
            categories.name AS category_name,
            products.purchase_price,
            products.selling_price,
            products.stock_quantity,
            products.minimum_stock,
            products.description,
            products.created_at,
            products.updated_at
        FROM products
        INNER JOIN categories
            ON products.category_id = categories.id
        ORDER BY products.id DESC
    """

    try:

        cursor.execute(query)

        products = cursor.fetchall()

        return jsonify(products), 200

    except mysql.connector.Error as error:

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Add Product
# =========================


@app.route("/api/products", methods=["POST"])
def add_product():

    data = request.get_json()

    product_name = data.get("product_name")
    sku = data.get("sku")
    category_id = data.get("category_id")
    purchase_price = data.get("purchase_price")
    selling_price = data.get("selling_price")
    stock_quantity = data.get("stock_quantity", 0)
    minimum_stock = data.get("minimum_stock", 5)
    description = data.get("description", "")

    # Validate required fields
    if not product_name or not sku or not category_id:

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Product name, SKU and category are required",
                }
            ),
            400,
        )

    db = get_db_connection()
    cursor = db.cursor()

    query = """
        INSERT INTO products (
            product_name,
            sku,
            category_id,
            purchase_price,
            selling_price,
            stock_quantity,
            minimum_stock,
            description
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        product_name,
        sku,
        category_id,
        purchase_price,
        selling_price,
        stock_quantity,
        minimum_stock,
        description,
    )

    try:

        cursor.execute(query, values)

        db.commit()

        product_id = cursor.lastrowid

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Product added successfully",
                    "product_id": product_id,
                }
            ),
            201,
        )

    except mysql.connector.IntegrityError:

        db.rollback()

        return jsonify({"success": False, "message": "SKU already exists"}), 409

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Get One Product
# =========================


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            products.id,
            products.product_name,
            products.sku,
            products.category_id,
            categories.name AS category_name,
            products.purchase_price,
            products.selling_price,
            products.stock_quantity,
            products.minimum_stock,
            products.description,
            products.created_at,
            products.updated_at
        FROM products
        INNER JOIN categories
            ON products.category_id = categories.id
        WHERE products.id = %s
    """

    try:

        cursor.execute(query, (product_id,))

        product = cursor.fetchone()

        if not product:

            return jsonify({"success": False, "message": "Product not found"}), 404

        return jsonify({"success": True, "product": product}), 200

    except mysql.connector.Error as error:

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Update Product
# =========================


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):

    data = request.get_json()

    product_name = data.get("product_name")
    sku = data.get("sku")
    category_id = data.get("category_id")
    purchase_price = data.get("purchase_price")
    selling_price = data.get("selling_price")
    stock_quantity = data.get("stock_quantity")
    minimum_stock = data.get("minimum_stock")
    description = data.get("description", "")

    # Validate required fields
    if not product_name or not sku or not category_id:

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Product name, SKU and category are required",
                }
            ),
            400,
        )

    db = get_db_connection()
    cursor = db.cursor()

    try:

        # Check if product exists
        cursor.execute(
            """
            SELECT id
            FROM products
            WHERE id = %s
            """,
            (product_id,),
        )

        product = cursor.fetchone()

        if not product:

            return jsonify({"success": False, "message": "Product not found"}), 404

        query = """
            UPDATE products
            SET
                product_name = %s,
                sku = %s,
                category_id = %s,
                purchase_price = %s,
                selling_price = %s,
                stock_quantity = %s,
                minimum_stock = %s,
                description = %s
            WHERE id = %s
        """

        values = (
            product_name,
            sku,
            category_id,
            purchase_price,
            selling_price,
            stock_quantity,
            minimum_stock,
            description,
            product_id,
        )

        cursor.execute(query, values)

        db.commit()

        return (
            jsonify({"success": True, "message": "Product updated successfully"}),
            200,
        )

    except mysql.connector.IntegrityError:

        db.rollback()

        return jsonify({"success": False, "message": "SKU already exists"}), 409

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Delete Product
# =========================


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):

    db = get_db_connection()
    cursor = db.cursor()

    try:

        # Check if product exists
        cursor.execute(
            """
            SELECT id
            FROM products
            WHERE id = %s
            """,
            (product_id,),
        )

        product = cursor.fetchone()

        if not product:

            return jsonify({"success": False, "message": "Product not found"}), 404

        cursor.execute(
            """
            DELETE FROM products
            WHERE id = %s
            """,
            (product_id,),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Product deleted successfully"}),
            200,
        )

    except mysql.connector.IntegrityError:

        db.rollback()

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Product cannot be deleted because it is being used",
                }
            ),
            409,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Stock Page
# =========================


@app.route("/stock")
def stock():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("stock.html", full_name=full_name)


# =========================
# Stock API
# =========================


@app.route("/api/stock", methods=["GET"])
def get_stock():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
        SELECT
            products.id,
            products.product_name,
            products.sku,
            products.category_id,
            categories.name AS category_name,
            products.stock_quantity,
            products.minimum_stock
        FROM products
        INNER JOIN categories
            ON products.category_id = categories.id
        ORDER BY products.id DESC
    """

    try:

        cursor.execute(query)

        stock = cursor.fetchall()

        return jsonify({"success": True, "stock": stock}), 200

    except mysql.connector.Error as error:

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Update Stock
# =========================


@app.route("/api/stock/<int:product_id>", methods=["PUT"])
def update_stock(product_id):

    data = request.get_json()

    quantity = data.get("quantity")
    action = data.get("action")

    # Validate quantity

    if quantity is None:

        return jsonify({"success": False, "message": "Quantity is required."}), 400

    try:

        quantity = int(quantity)

    except (TypeError, ValueError):

        return (
            jsonify({"success": False, "message": "Quantity must be a valid number."}),
            400,
        )

    if quantity <= 0:

        return (
            jsonify(
                {"success": False, "message": "Quantity must be greater than zero."}
            ),
            400,
        )

    # Validate action

    if action not in ["in", "out"]:

        return jsonify({"success": False, "message": "Invalid stock action."}), 400

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # Get current stock

        cursor.execute(
            """
            SELECT
                id,
                product_name,
                stock_quantity
            FROM products
            WHERE id = %s
            """,
            (product_id,),
        )

        product = cursor.fetchone()

        if not product:

            return jsonify({"success": False, "message": "Product not found."}), 404

        current_stock = int(product["stock_quantity"])

        # =========================
        # Stock In
        # =========================

        if action == "in":

            new_stock = current_stock + quantity

            message = f"{quantity} units added successfully."

        # =========================
        # Stock Out
        # =========================

        else:

            if quantity > current_stock:

                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Stock Out quantity cannot be greater than current stock.",
                        }
                    ),
                    400,
                )

            new_stock = current_stock - quantity

            message = f"{quantity} units removed successfully."

        # Update database

        cursor.execute(
            """
            UPDATE products
            SET stock_quantity = %s
            WHERE id = %s
            """,
            (new_stock, product_id),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": message, "new_stock": new_stock}),
            200,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Customers
# =========================


@app.route("/customers")
def customers():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("customers.html", full_name=full_name)


# =========================
# GET — Load all customers
# =========================


@app.route("/api/customers", methods=["GET"])
def get_customers():

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                id,
                customer_name,
                phone,
                email,
                address,
                created_at,
                updated_at
            FROM customers
            ORDER BY id DESC
        """)

        customers = cursor.fetchall()

        return jsonify({"success": True, "customers": customers}), 200

    except mysql.connector.Error as error:

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# POST — Add Customer
# =========================
@app.route("/api/customers", methods=["POST"])
def add_customer():

    data = request.get_json()

    customer_name = data.get("customer_name")
    phone = data.get("phone")
    email = data.get("email")
    address = data.get("address")

    if not customer_name or not customer_name.strip():

        return jsonify({"success": False, "message": "Customer name is required."}), 400

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO customers
            (
                customer_name,
                phone,
                email,
                address
            )
            VALUES (%s, %s, %s, %s)
        """,
            (customer_name.strip(), phone, email, address),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Customer added successfully."}),
            201,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# PUT — Update Customer
# =========================
@app.route("/api/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):

    data = request.get_json()

    customer_name = data.get("customer_name")
    phone = data.get("phone")
    email = data.get("email")
    address = data.get("address")

    if not customer_name or not customer_name.strip():

        return jsonify({"success": False, "message": "Customer name is required."}), 400

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:

        # Check customer exists

        cursor.execute(
            """
            SELECT id
            FROM customers
            WHERE id = %s
        """,
            (customer_id,),
        )

        customer = cursor.fetchone()

        if not customer:

            return jsonify({"success": False, "message": "Customer not found."}), 404

        # Update customer

        cursor.execute(
            """
            UPDATE customers

            SET
                customer_name = %s,
                phone = %s,
                email = %s,
                address = %s

            WHERE id = %s
        """,
            (customer_name.strip(), phone, email, address, customer_id),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Customer updated successfully."}),
            200,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Delete Customer
# =========================
@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):

    db = get_db_connection()
    cursor = db.cursor()

    try:

        # Check if customer exists
        cursor.execute(
            """
            SELECT id
            FROM customers
            WHERE id = %s
            """,
            (customer_id,),
        )

        customer = cursor.fetchone()

        if not customer:
            return jsonify({"success": False, "message": "Customer not found."}), 404

        # Delete customer
        cursor.execute(
            """
            DELETE FROM customers
            WHERE id = %s
            """,
            (customer_id,),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Customer deleted successfully."}),
            200,
        )

    except mysql.connector.Error as error:

        db.rollback()

        return jsonify({"success": False, "message": str(error)}), 500

    finally:

        cursor.close()
        db.close()


# =========================
# Sales
# =========================
@app.route("/sales")
def sales():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("sales.html", full_name=full_name)


# ===============================
# CREATE SALE
# ===============================


@app.route("/api/sales", methods=["POST"])
def create_sale():

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No sale data received."}), 400

    customer_id = data.get("customer_id")
    total_amount = data.get("total_amount", 0)
    discount = data.get("discount", 0)
    final_amount = data.get("final_amount", 0)
    items = data.get("items", [])

    # ===============================
    # BASIC VALIDATION
    # ===============================

    if not items:
        return (
            jsonify(
                {"success": False, "message": "Sale must contain at least one product."}
            ),
            400,
        )

    try:

        total_amount = float(total_amount)
        discount = float(discount)
        final_amount = float(final_amount)

    except (TypeError, ValueError):

        return jsonify({"success": False, "message": "Invalid sale amount."}), 400

    if total_amount < 0 or discount < 0 or final_amount < 0:

        return (
            jsonify({"success": False, "message": "Sale amounts cannot be negative."}),
            400,
        )

    if discount > total_amount:

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Discount cannot be greater than subtotal.",
                }
            ),
            400,
        )

    db = None
    cursor = None

    try:

        # ===============================
        # DATABASE CONNECTION
        # ===============================

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        # ===============================
        # CHECK CUSTOMER
        # ===============================

        if customer_id:

            cursor.execute(
                """
                SELECT id
                FROM customers
                WHERE id = %s
                """,
                (customer_id,),
            )

            customer = cursor.fetchone()

            if not customer:

                return (
                    jsonify({"success": False, "message": "Customer not found."}),
                    404,
                )

        # ===============================
        # CHECK PRODUCTS + STOCK
        # ===============================

        checked_items = []

        calculated_total = 0

        for item in items:

            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if not product_id or not quantity:

                db.rollback()

                return jsonify({"success": False, "message": "Invalid sale item."}), 400

            try:

                product_id = int(product_id)
                quantity = int(quantity)

            except (TypeError, ValueError):

                db.rollback()

                return (
                    jsonify(
                        {"success": False, "message": "Invalid product or quantity."}
                    ),
                    400,
                )

            if quantity <= 0:

                db.rollback()

                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Quantity must be greater than zero.",
                        }
                    ),
                    400,
                )

            cursor.execute(
                """
                SELECT
                    id,
                    product_name,
                    selling_price,
                    stock_quantity
                FROM products
                WHERE id = %s
                FOR UPDATE
                """,
                (product_id,),
            )

            product = cursor.fetchone()

            if not product:

                db.rollback()

                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"Product with ID {product_id} not found.",
                        }
                    ),
                    404,
                )

            available_stock = int(product["stock_quantity"] or 0)

            if quantity > available_stock:

                db.rollback()

                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f"Only {available_stock} units of "
                            f"{product['product_name']} are available.",
                        }
                    ),
                    400,
                )

            unit_price = float(product["selling_price"] or 0)

            subtotal = unit_price * quantity

            calculated_total += subtotal

            checked_items.append(
                {
                    "product_id": product["id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "subtotal": subtotal,
                }
            )

        # ===============================
        # VERIFY TOTAL
        # ===============================

        calculated_final = calculated_total - discount

        if abs(calculated_final - final_amount) > 0.01:

            db.rollback()

            return jsonify({"success": False, "message": "Sale total is invalid."}), 400

        # ===============================
        # CREATE SALE
        # ===============================

        cursor.execute(
            """
            INSERT INTO sales
                (
                    customer_id,
                    total_amount,
                    discount,
                    final_amount
                )
            VALUES
                (%s, %s, %s, %s)
            """,
            (customer_id, calculated_total, discount, calculated_final),
        )

        sale_id = cursor.lastrowid

        # ===============================
        # CREATE SALE ITEMS
        # ===============================

        for item in checked_items:

            cursor.execute(
                """
                INSERT INTO sale_items
                    (
                        sale_id,
                        product_id,
                        quantity,
                        unit_price,
                        subtotal
                    )
                VALUES
                    (%s, %s, %s, %s, %s)
                """,
                (
                    sale_id,
                    item["product_id"],
                    item["quantity"],
                    item["unit_price"],
                    item["subtotal"],
                ),
            )

            # ===============================
            # DEDUCT STOCK
            # ===============================

            cursor.execute(
                """
                UPDATE products
                SET stock_quantity =
                    stock_quantity - %s
                WHERE id = %s
                """,
                (item["quantity"], item["product_id"]),
            )

        # ===============================
        # COMMIT TRANSACTION
        # ===============================

        db.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Sale completed successfully.",
                    "sale_id": sale_id,
                }
            ),
            201,
        )

    except mysql.connector.Error as error:

        if db:
            db.rollback()

        print("Create sale database error:", error)

        return (
            jsonify(
                {"success": False, "message": "Database error while creating sale."}
            ),
            500,
        )

    except Exception as error:

        if db:
            db.rollback()

        print("Create sale error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while creating the sale.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ===============================
# SALES HISTORY PAGE
# ===============================


@app.route("/sales-history")
def sales_history():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("sales-history.html", full_name=full_name)


# ===============================
# GET SALES HISTORY
# ===============================


@app.route("/api/sales", methods=["GET"])
def get_sales():

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                s.id,
                s.customer_id,

                COALESCE(
                    c.customer_name,
                    'Walk-in Customer'
                ) AS customer_name,

                s.total_amount,
                s.discount,
                s.final_amount,
                s.created_at

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.id

            ORDER BY s.created_at DESC
            """)

        sales = cursor.fetchall()

        return jsonify({"success": True, "sales": sales}), 200

    except mysql.connector.Error as error:

        print("Sales history database error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database error while loading sales history.",
                }
            ),
            500,
        )

    except Exception as error:

        print("Sales history error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while loading sales history.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ===============================
# GET SINGLE SALE DETAILS
# ===============================


@app.route("/api/sales/<int:sale_id>", methods=["GET"])
def get_sale_details(sale_id):

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        # ===============================
        # SALE INFORMATION
        # ===============================

        cursor.execute(
            """
            SELECT
                s.id,
                s.customer_id,

                COALESCE(
                    c.customer_name,
                    'Walk-in Customer'
                ) AS customer_name,

                s.total_amount,
                s.discount,
                s.final_amount,
                s.created_at

            FROM sales s

            LEFT JOIN customers c
                ON s.customer_id = c.id

            WHERE s.id = %s
            """,
            (sale_id,),
        )

        sale = cursor.fetchone()

        if not sale:

            return jsonify({"success": False, "message": "Sale not found."}), 404

        # ===============================
        # SALE ITEMS
        # ===============================

        cursor.execute(
            """
            SELECT
                si.id,
                si.product_id,

                p.product_name,
                p.sku,

                si.quantity,
                si.unit_price,
                si.subtotal

            FROM sale_items si

            INNER JOIN products p
                ON si.product_id = p.id

            WHERE si.sale_id = %s

            ORDER BY si.id ASC
            """,
            (sale_id,),
        )

        items = cursor.fetchall()

        return jsonify({"success": True, "sale": sale, "items": items}), 200

    except mysql.connector.Error as error:

        print("Sale details database error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database error while loading sale details.",
                }
            ),
            500,
        )

    except Exception as error:

        print("Sale details error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while loading sale details.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================
# Settings
# =========================
@app.route("/settings")
def settings():
    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("settings.html", full_name=full_name)


# ========================================
# SETTINGS - GET PROFILE
# ========================================


@app.route("/api/settings/profile", methods=["GET"])
def get_settings_profile():

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    db = None
    cursor = None

    try:

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                fullname,
                username,
                email,
                phone
            FROM users
            WHERE id = %s
            """,
            (session["user_id"],),
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "User not found."}), 404

        return jsonify({"success": True, "user": user}), 200

    except mysql.connector.Error as error:

        print("Settings profile database error:", error)

        return (
            jsonify(
                {"success": False, "message": "Database error while loading profile."}
            ),
            500,
        )

    except Exception as error:

        print("Settings profile error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while loading profile.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ========================================
# SETTINGS - UPDATE PROFILE
# ========================================


@app.route("/api/settings/profile", methods=["PUT"])
def update_settings_profile():

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    full_name = data.get("fullName", "").strip()
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()

    if not full_name or not username or not email:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Full name, username and email are required.",
                }
            ),
            400,
        )

    db = None
    cursor = None

    try:

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Check username/email already used by another user

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE (username = %s OR email = %s)
            AND id != %s
            """,
            (username, email, session["user_id"]),
        )

        existing_user = cursor.fetchone()

        if existing_user:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Username or email is already in use.",
                    }
                ),
                409,
            )

        # Update profile

        cursor.execute(
            """
            UPDATE users
            SET
                fullname = %s,
                username = %s,
                email = %s,
                phone = %s
            WHERE id = %s
            """,
            (full_name, username, email, phone, session["user_id"]),
        )

        db.commit()

        # Update session username

        session["username"] = username

        return (
            jsonify({"success": True, "message": "Profile updated successfully."}),
            200,
        )

    except mysql.connector.Error as error:

        if db:
            db.rollback()

        print("Settings profile update database error:", error)

        return (
            jsonify(
                {"success": False, "message": "Database error while updating profile."}
            ),
            500,
        )

    except Exception as error:

        if db:
            db.rollback()

        print("Settings profile update error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while updating profile.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ========================================
# SETTINGS - CHANGE PASSWORD
# ========================================


@app.route("/api/settings/password", methods=["PUT"])
def change_password():

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    current_password = data.get("currentPassword", "")
    new_password = data.get("newPassword", "")
    confirm_password = data.get("confirmPassword", "")

    # Required fields

    if not current_password or not new_password or not confirm_password:
        return (
            jsonify({"success": False, "message": "All password fields are required."}),
            400,
        )

    # Confirm new password

    if new_password != confirm_password:
        return (
            jsonify({"success": False, "message": "New passwords do not match."}),
            400,
        )

    # Password length

    if len(new_password) < 7:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "New password must be at least 7 characters long.",
                }
            ),
            400,
        )

    db = None
    cursor = None

    try:

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # Get current password hash

        cursor.execute(
            """
            SELECT password
            FROM users
            WHERE id = %s
            """,
            (session["user_id"],),
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({"success": False, "message": "User not found."}), 404

        # Check current password

        if not check_password_hash(user["password"], current_password):
            return (
                jsonify(
                    {"success": False, "message": "Current password is incorrect."}
                ),
                401,
            )

        # Don't allow same password

        if check_password_hash(user["password"], new_password):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "New password must be different from the current password.",
                    }
                ),
                400,
            )

        # Hash new password

        new_password_hash = generate_password_hash(new_password)

        # Update password

        cursor.execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (new_password_hash, session["user_id"]),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Password changed successfully."}),
            200,
        )

    except mysql.connector.Error as error:

        if db:
            db.rollback()

        print("Password change database error:", error)

        return (
            jsonify(
                {"success": False, "message": "Database error while changing password."}
            ),
            500,
        )

    except Exception as error:

        if db:
            db.rollback()

        print("Password change error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while changing password.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ========================================
# SETTINGS - GET BUSINESS INFORMATION
# ========================================


@app.route("/api/settings/business", methods=["GET"])
def get_business_settings():

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    db = None
    cursor = None

    try:

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                business_name,
                business_phone,
                business_email,
                currency,
                business_address
            FROM business_settings
            ORDER BY id ASC
            LIMIT 1
            """)

        business = cursor.fetchone()

        if not business:
            return (
                jsonify({"success": False, "message": "Business settings not found."}),
                404,
            )

        return jsonify({"success": True, "business": business}), 200

    except mysql.connector.Error as error:

        print("Business settings database error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database error while loading business information.",
                }
            ),
            500,
        )

    except Exception as error:

        print("Business settings error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while loading business information.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# ========================================
# SETTINGS - UPDATE BUSINESS INFORMATION
# ========================================


@app.route("/api/settings/business", methods=["PUT"])
def update_business_settings():

    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first."}), 401

    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received."}), 400

    business_name = data.get("businessName", "").strip()
    business_phone = data.get("businessPhone", "").strip()
    business_email = data.get("businessEmail", "").strip()
    currency = data.get("currency", "PKR").strip()
    business_address = data.get("businessAddress", "").strip()

    if not business_name:
        return jsonify({"success": False, "message": "Business name is required."}), 400

    # Validate email only if provided

    if business_email:

        import re

        email_pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"

        if not re.match(email_pattern, business_email):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Please enter a valid business email.",
                    }
                ),
                400,
            )

    db = None
    cursor = None

    try:

        db = get_db_connection()
        cursor = db.cursor()

        # Check whether settings already exist

        cursor.execute("""
            SELECT id
            FROM business_settings
            ORDER BY id ASC
            LIMIT 1
            """)

        existing_settings = cursor.fetchone()

        if existing_settings:

            # Update existing record

            cursor.execute(
                """
                UPDATE business_settings
                SET
                    business_name = %s,
                    business_phone = %s,
                    business_email = %s,
                    currency = %s,
                    business_address = %s
                WHERE id = %s
                """,
                (
                    business_name,
                    business_phone,
                    business_email,
                    currency,
                    business_address,
                    existing_settings[0],
                ),
            )

        else:

            # Create settings if no record exists

            cursor.execute(
                """
                INSERT INTO business_settings (
                    business_name,
                    business_phone,
                    business_email,
                    currency,
                    business_address
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    business_name,
                    business_phone,
                    business_email,
                    currency,
                    business_address,
                ),
            )

        db.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Business information updated successfully.",
                }
            ),
            200,
        )

    except mysql.connector.Error as error:

        if db:
            db.rollback()

        print("Business settings update database error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database error while updating business information.",
                }
            ),
            500,
        )

    except Exception as error:

        if db:
            db.rollback()

        print("Business settings update error:", error)

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Something went wrong while updating business information.",
                }
            ),
            500,
        )

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================
# Run Flask
# =========================

if __name__ == "__main__":
    app.run(debug=True)
