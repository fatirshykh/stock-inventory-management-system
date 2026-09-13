from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv
import os
import re

# =========================
# LOAD ENVIRONMENT VARIABLES
# =========================

load_dotenv()


# =========================
# FLASK APP
# =========================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


# =========================
# SUPABASE DATABASE
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


# =========================
# JSON SAFE CONVERTER
# =========================


def make_json_safe(value):

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, list):
        return [make_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {key: make_json_safe(item) for key, item in value.items()}

    return value


# =========================
# GENERATE PROFESSIONAL INVOICE IMAGE
# =========================


def generate_invoice_image(
    sale_id,
    customer_name,
    items,
    subtotal,
    discount,
    final_amount,
    currency="PKR",
):

    bills_folder = os.path.join(app.root_path, "static", "bills")
    os.makedirs(bills_folder, exist_ok=True)

    # =========================
    # IMAGE SETTINGS
    # =========================

    width = 1200
    margin = 70

    header_height = 270
    table_header_height = 65
    row_height = 72

    # Calculate dynamic height
    image_height = header_height + table_header_height + (len(items) * row_height) + 430

    image = Image.new("RGB", (width, image_height), (248, 249, 251))

    draw = ImageDraw.Draw(image)

    # =========================
    # FONTS
    # =========================

    try:

        regular_font_path = "C:/Windows/Fonts/arial.ttf"
        bold_font_path = "C:/Windows/Fonts/arialbd.ttf"

        logo_font = ImageFont.truetype(bold_font_path, 58)

        invoice_title_font = ImageFont.truetype(bold_font_path, 38)

        section_font = ImageFont.truetype(bold_font_path, 25)

        table_header_font = ImageFont.truetype(bold_font_path, 21)

        regular_font = ImageFont.truetype(regular_font_path, 22)

        small_font = ImageFont.truetype(regular_font_path, 19)

        bold_font = ImageFont.truetype(bold_font_path, 22)

        total_font = ImageFont.truetype(bold_font_path, 34)

        footer_font = ImageFont.truetype(bold_font_path, 22)

    except Exception:

        logo_font = ImageFont.load_default()
        invoice_title_font = ImageFont.load_default()
        section_font = ImageFont.load_default()
        table_header_font = ImageFont.load_default()
        regular_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
        total_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()

    # =========================
    # COLORS
    # =========================

    background = (248, 249, 251)
    white = (255, 255, 255)

    black = (24, 24, 27)
    dark_gray = (55, 55, 60)
    gray = (105, 105, 112)
    light_gray = (235, 236, 239)
    border_gray = (218, 220, 224)

    red = (220, 38, 38)
    light_red = (254, 226, 226)

    green = (22, 163, 74)

    # =========================
    # MAIN WHITE CARD
    # =========================

    card_left = margin
    card_top = 35
    card_right = width - margin
    card_bottom = image_height - 35

    draw.rounded_rectangle(
        (card_left, card_top, card_right, card_bottom),
        radius=18,
        fill=white,
        outline=border_gray,
        width=2,
    )

    # =========================
    # HEADER
    # =========================

    center_x = width // 2

    # SIMS logo
    logo_text = "SIMS"

    bbox = draw.textbbox((0, 0), logo_text, font=logo_font)

    logo_width = bbox[2] - bbox[0]

    draw.text((center_x - logo_width / 2, 70), logo_text, fill=red, font=logo_font)

    # System name
    system_name = "Smart Inventory & Sales Management System"

    bbox = draw.textbbox((0, 0), system_name, font=small_font)

    system_width = bbox[2] - bbox[0]

    draw.text(
        (center_x - system_width / 2, 140), system_name, fill=gray, font=small_font
    )

    # Red separator
    draw.rounded_rectangle(
        (card_left + 35, 185, card_right - 35, 190), radius=3, fill=red
    )

    # Invoice title
    draw.text((card_left + 35, 215), "INVOICE", fill=black, font=invoice_title_font)

    invoice_number = f"#{sale_id}"

    bbox = draw.textbbox((0, 0), invoice_number, font=invoice_title_font)

    invoice_width = bbox[2] - bbox[0]

    draw.text(
        (card_right - 35 - invoice_width, 215),
        invoice_number,
        fill=red,
        font=invoice_title_font,
    )

    # =========================
    # CUSTOMER INFORMATION
    # =========================

    y = 285

    date_text = datetime.now().strftime("%d %b %Y  •  %I:%M %p")

    draw.text((card_left + 35, y), f"Date: {date_text}", fill=gray, font=small_font)

    customer_display = customer_name or "Walk-in Customer"

    draw.text((card_right - 430, y), "Customer:", fill=gray, font=small_font)

    draw.text(
        (card_right - 305, y),
        str(customer_display)[:25],
        fill=dark_gray,
        font=bold_font,
    )

    # =========================
    # TABLE
    # =========================

    table_top = 335

    table_left = card_left + 35
    table_right = card_right - 35

    # Column positions
    product_x = table_left + 20
    sku_x = table_left + 500
    qty_x = table_left + 665
    price_x = table_left + 755
    total_x = table_left + 925

    # Table header
    draw.rounded_rectangle(
        (table_left, table_top, table_right, table_top + table_header_height),
        radius=8,
        fill=(245, 245, 247),
    )

    draw.text(
        (product_x, table_top + 20), "PRODUCT", fill=black, font=table_header_font
    )

    draw.text((sku_x, table_top + 20), "SKU", fill=black, font=table_header_font)

    draw.text((qty_x, table_top + 20), "QTY", fill=black, font=table_header_font)

    draw.text((price_x, table_top + 20), "PRICE", fill=black, font=table_header_font)

    draw.text((total_x, table_top + 20), "TOTAL", fill=black, font=table_header_font)

    y = table_top + table_header_height

    # =========================
    # SALE ITEMS
    # =========================

    for index, item in enumerate(items):

        product_name = str(item.get("product_name", ""))

        sku = str(item.get("sku", "-"))

        quantity = int(item.get("quantity", 0))

        unit_price = float(item.get("unit_price", 0))

        item_subtotal = float(item.get("subtotal", 0))

        # Alternate row background
        if index % 2 == 0:
            draw.rectangle(
                (table_left, y, table_right, y + row_height), fill=(252, 252, 253)
            )

        # Bottom border
        draw.line(
            (table_left, y + row_height, table_right, y + row_height),
            fill=border_gray,
            width=1,
        )

        # Product
        draw.text(
            (product_x, y + 23), product_name[:32], fill=dark_gray, font=regular_font
        )

        # SKU
        draw.text((sku_x, y + 23), sku[:14], fill=gray, font=small_font)

        # Quantity
        draw.text((qty_x, y + 23), str(quantity), fill=dark_gray, font=regular_font)

        # Unit price
        price_text = f"{currency} {unit_price:,.0f}"

        draw.text((price_x, y + 23), price_text, fill=dark_gray, font=small_font)

        # Total
        total_text = f"{currency} {item_subtotal:,.0f}"

        draw.text((total_x, y + 23), total_text, fill=dark_gray, font=small_font)

        y += row_height

    # =========================
    # TOTALS SECTION
    # =========================

    y += 35

    totals_left = table_left + 590
    totals_right = table_right

    # Subtotal
    draw.text((totals_left, y), "Subtotal", fill=gray, font=regular_font)

    subtotal_text = f"{currency} {float(subtotal):,.2f}"

    bbox = draw.textbbox((0, 0), subtotal_text, font=regular_font)

    subtotal_width = bbox[2] - bbox[0]

    draw.text(
        (totals_right - subtotal_width, y),
        subtotal_text,
        fill=dark_gray,
        font=regular_font,
    )

    # Discount
    y += 48

    discount_amount = float(discount)

    discount_percentage = (
        (discount_amount / float(subtotal)) * 100 if float(subtotal) > 0 else 0
    )

    discount_label = f"Discount ({discount_percentage:.2f}%)"

    draw.text((totals_left, y), discount_label, fill=gray, font=regular_font)

    discount_text = f"- {currency} {discount_amount:,.2f}"

    bbox = draw.textbbox((0, 0), discount_text, font=regular_font)

    discount_width = bbox[2] - bbox[0]

    draw.text(
        (totals_right - discount_width, y), discount_text, fill=green, font=regular_font
    )

    # Total separator
    y += 55

    draw.line((totals_left, y, totals_right, y), fill=border_gray, width=2)

    # Final total background
    y += 20

    total_box_top = y
    total_box_bottom = y + 70

    draw.rounded_rectangle(
        (totals_left - 20, total_box_top, totals_right, total_box_bottom),
        radius=10,
        fill=light_red,
    )

    draw.text((totals_left, y + 17), "TOTAL", fill=black, font=total_font)

    final_text = f"{currency} {float(final_amount):,.2f}"

    bbox = draw.textbbox((0, 0), final_text, font=total_font)

    final_width = bbox[2] - bbox[0]

    draw.text(
        (totals_right - final_width - 20, y + 17), final_text, fill=red, font=total_font
    )

    # =========================
    # FOOTER
    # =========================

    footer_y = total_box_bottom + 55

    footer_text = "Thank you for your business!"

    bbox = draw.textbbox((0, 0), footer_text, font=footer_font)

    footer_width = bbox[2] - bbox[0]

    draw.text(
        (center_x - footer_width / 2, footer_y),
        footer_text,
        fill=black,
        font=footer_font,
    )

    footer_subtitle = "Powered by SIMS"

    bbox = draw.textbbox((0, 0), footer_subtitle, font=small_font)

    footer_width = bbox[2] - bbox[0]

    draw.text(
        (center_x - footer_width / 2, footer_y + 38),
        footer_subtitle,
        fill=gray,
        font=small_font,
    )

    # =========================
    # SAVE IMAGE
    # =========================

    invoice_filename = f"invoice_{sale_id}.png"

    invoice_path = os.path.join(bills_folder, invoice_filename)

    image.save(invoice_path, "PNG", optimize=True)

    return f"/static/bills/{invoice_filename}"


# ============================================================
# HOME / LOGIN PAGE
# ============================================================


@app.route("/")
def home():
    return render_template("login.html")


# ============================================================
# SIGNUP PAGE
# ============================================================


@app.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")


# ============================================================
# SIGNUP
# ============================================================


@app.route("/signup", methods=["POST"])
def signup():

    data = request.get_json()

    fullname = data["fullname"]
    username = data["username"]
    email = data["email"]
    phone = data["phone"]
    password = data["password"]

    password = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users
            (
                fullname,
                username,
                email,
                phone,
                password
            )
            VALUES
            (%s, %s, %s, %s, %s)
            """,
            (fullname, username, email, phone, password),
        )

        db.commit()

        return jsonify({"success": True, "message": "Account created successfully."})

    except psycopg2.IntegrityError:

        db.rollback()

        return (
            jsonify({"success": False, "message": "Username or email already exists."}),
            409,
        )

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# LOGIN PAGE
# ============================================================


@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")


# ============================================================
# LOGIN
# ============================================================


@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data["username"]
    password = data["password"]

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

    try:

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE username = %s
               OR email = %s
            """,
            (username, username),
        )

        user = cursor.fetchone()

        if user:

            if check_password_hash(user["password"], password):

                session["user_id"] = user["id"]
                session["username"] = user["username"]

                return jsonify({"success": True, "message": "Login successful."})

        return (
            jsonify(
                {"success": False, "message": "Invalid username/email or password."}
            ),
            401,
        )

    except psycopg2.Error as error:

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# DASHBOARD
# ============================================================


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("dashboard.html", full_name=full_name)


# ============================================================
# LOGOUT
# ============================================================


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ============================================================
# DASHBOARD STATS
# ============================================================


@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(cursor_factory=RealDictCursor)

        # TOTAL PRODUCTS

        cursor.execute("""
            SELECT COUNT(*) AS total_products
            FROM products
            """)

        total_products = cursor.fetchone()["total_products"]

        # TOTAL CATEGORIES

        cursor.execute("""
            SELECT COUNT(*) AS total_categories
            FROM categories
            """)

        total_categories = cursor.fetchone()["total_categories"]

        # TOTAL CUSTOMERS

        cursor.execute("""
            SELECT COUNT(*) AS total_customers
            FROM customers
            """)

        total_customers = cursor.fetchone()["total_customers"]

        # LOW STOCK

        cursor.execute("""
            SELECT COUNT(*) AS low_stock
            FROM products
            WHERE stock_quantity <= minimum_stock
            """)

        low_stock = cursor.fetchone()["low_stock"]

        # TODAY SALES

        cursor.execute("""
            SELECT
                COALESCE(
                    SUM(final_amount),
                    0
                ) AS today_sales
            FROM sales
            WHERE DATE(created_at) = CURRENT_DATE
            """)

        today_sales = cursor.fetchone()["today_sales"]

        # RECENT SALES

        cursor.execute("""
            SELECT
                s.id AS invoice,

                COALESCE(
                    c.customer_name,
                    'Walk-in Customer'
                ) AS customer,

                TO_CHAR(
                    s.created_at,
                    'DD Mon YYYY'
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

        # LOW STOCK PRODUCTS

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

        return (
            jsonify(
                make_json_safe(
                    {
                        "success": True,
                        "total_products": total_products,
                        "total_categories": total_categories,
                        "total_customers": total_customers,
                        "low_stock": low_stock,
                        "today_sales": today_sales or 0,
                        "recent_sales": recent_sales,
                        "low_stock_products": low_stock_products,
                    }
                )
            ),
            200,
        )

    except psycopg2.Error as error:

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


# ============================================================
# CATEGORIES PAGE
# ============================================================


@app.route("/categories")
def categories():
    return render_template("categories.html")


# ============================================================
# GET ALL CATEGORIES
# ============================================================


@app.route("/api/categories", methods=["GET"])
def get_categories():

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

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

        return jsonify(make_json_safe({"success": True, "categories": categories})), 200

    except psycopg2.Error as error:

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# GET ONE CATEGORY
# ============================================================


@app.route("/api/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

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

            return (jsonify({"success": False, "message": "Category not found."}), 404)

        return jsonify(make_json_safe({"success": True, "category": category})), 200

    except psycopg2.Error as error:

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# CREATE CATEGORY
# ============================================================


@app.route("/api/categories", methods=["POST"])
def create_category():

    data = request.get_json()

    name = data.get("name", "").strip()

    description = data.get("description", "").strip()

    status = data.get("status", "active")

    if not name:

        return (
            jsonify({"success": False, "message": "Category name is required."}),
            400,
        )

    db = get_db_connection()
    cursor = db.cursor()

    try:

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

            db.rollback()

            return (
                jsonify({"success": False, "message": "Category already exists."}),
                409,
            )

        cursor.execute(
            """
            INSERT INTO categories
            (
                name,
                description,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (name, description, status),
        )

        category_id = cursor.fetchone()[0]

        db.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Category created successfully.",
                    "category_id": category_id,
                }
            ),
            201,
        )

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# UPDATE CATEGORY
# ============================================================


@app.route("/api/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):

    data = request.get_json()

    name = data.get("name", "").strip()

    description = data.get("description", "").strip()

    status = data.get("status", "active")

    if not name:

        return (
            jsonify({"success": False, "message": "Category name is required."}),
            400,
        )

    db = get_db_connection()

    cursor = db.cursor()

    try:

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

            db.rollback()

            return (jsonify({"success": False, "message": "Category not found."}), 404)

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

            db.rollback()

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
                status = %s,
                updated_at = NOW()

            WHERE id = %s
            """,
            (name, description, status, category_id),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Category updated successfully."}),
            200,
        )

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# DELETE CATEGORY
# ============================================================


@app.route("/api/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):

    db = get_db_connection()

    cursor = db.cursor()

    try:

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

            db.rollback()

            return (jsonify({"success": False, "message": "Category not found."}), 404)

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

    except psycopg2.IntegrityError:

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

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# PRODUCTS PAGE
# ============================================================


@app.route("/products")
def products():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("products.html", full_name=full_name)


# ============================================================
# GET ALL PRODUCTS
# ============================================================


@app.route("/api/products", methods=["GET"])
def get_products():

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

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

        return jsonify(make_json_safe(products)), 200

    except psycopg2.Error as error:

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# ADD PRODUCT
# ============================================================


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
        INSERT INTO products
        (
            product_name,
            sku,
            category_id,
            purchase_price,
            selling_price,
            stock_quantity,
            minimum_stock,
            description
        )

        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )

        RETURNING id
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

        product_id = cursor.fetchone()[0]

        db.commit()

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

    except psycopg2.IntegrityError:

        db.rollback()

        return (jsonify({"success": False, "message": "SKU already exists"}), 409)

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# GET ONE PRODUCT
# ============================================================


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

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

            return (jsonify({"success": False, "message": "Product not found"}), 404)

        return jsonify(make_json_safe({"success": True, "product": product})), 200

    except psycopg2.Error as error:

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# UPDATE PRODUCT
# ============================================================


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

            db.rollback()

            return (jsonify({"success": False, "message": "Product not found"}), 404)

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
                description = %s,
                updated_at = NOW()

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

    except psycopg2.IntegrityError:

        db.rollback()

        return (jsonify({"success": False, "message": "SKU already exists"}), 409)

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# DELETE PRODUCT
# ============================================================


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):

    db = get_db_connection()

    cursor = db.cursor()

    try:

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

            db.rollback()

            return (jsonify({"success": False, "message": "Product not found"}), 404)

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

    except psycopg2.IntegrityError:

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

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# STOCK PAGE
# ============================================================


@app.route("/stock")
def stock():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("stock.html", full_name=full_name)


# ============================================================
# STOCK API
# ============================================================


@app.route("/api/stock", methods=["GET"])
def get_stock():

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

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

        return jsonify(make_json_safe({"success": True, "stock": stock})), 200

    except psycopg2.Error as error:

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# UPDATE STOCK
# ============================================================


@app.route("/api/stock/<int:product_id>", methods=["PUT"])
def update_stock(product_id):

    data = request.get_json()

    quantity = data.get("quantity")

    action = data.get("action")

    if quantity is None:

        return (jsonify({"success": False, "message": "Quantity is required."}), 400)

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

    if action not in ["in", "out"]:

        return (jsonify({"success": False, "message": "Invalid stock action."}), 400)

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

    try:

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

            db.rollback()

            return (jsonify({"success": False, "message": "Product not found."}), 404)

        current_stock = int(product["stock_quantity"])

        if action == "in":

            new_stock = current_stock + quantity

            message = f"{quantity} units added successfully."

        else:

            if quantity > current_stock:

                db.rollback()

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

        cursor.execute(
            """
            UPDATE products

            SET
                stock_quantity = %s,
                updated_at = NOW()

            WHERE id = %s
            """,
            (new_stock, product_id),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": message, "new_stock": new_stock}),
            200,
        )

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# CUSTOMERS PAGE
# ============================================================


@app.route("/customers")
def customers():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("customers.html", full_name=full_name)


# ============================================================
# GET CUSTOMERS
# ============================================================


@app.route("/api/customers", methods=["GET"])
def get_customers():

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

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

        return jsonify(make_json_safe({"success": True, "customers": customers})), 200

    except psycopg2.Error as error:

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# ADD CUSTOMER
# ============================================================


@app.route("/api/customers", methods=["POST"])
def add_customer():

    data = request.get_json()

    customer_name = data.get("customer_name")

    phone = data.get("phone")

    email = data.get("email")

    address = data.get("address")

    if not customer_name or not customer_name.strip():

        return (
            jsonify({"success": False, "message": "Customer name is required."}),
            400,
        )

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

            VALUES
            (
                %s,
                %s,
                %s,
                %s
            )
            """,
            (customer_name.strip(), phone, email, address),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Customer added successfully."}),
            201,
        )

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# UPDATE CUSTOMER
# ============================================================


@app.route("/api/customers/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):

    data = request.get_json()

    customer_name = data.get("customer_name")

    phone = data.get("phone")

    email = data.get("email")

    address = data.get("address")

    if not customer_name or not customer_name.strip():

        return (
            jsonify({"success": False, "message": "Customer name is required."}),
            400,
        )

    db = get_db_connection()

    cursor = db.cursor(cursor_factory=RealDictCursor)

    try:

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

            db.rollback()

            return (jsonify({"success": False, "message": "Customer not found."}), 404)

        cursor.execute(
            """
            UPDATE customers

            SET
                customer_name = %s,
                phone = %s,
                email = %s,
                address = %s,
                updated_at = NOW()

            WHERE id = %s
            """,
            (customer_name.strip(), phone, email, address, customer_id),
        )

        db.commit()

        return (
            jsonify({"success": True, "message": "Customer updated successfully."}),
            200,
        )

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# DELETE CUSTOMER
# ============================================================


@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):

    db = get_db_connection()

    cursor = db.cursor()

    try:

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

            db.rollback()

            return (jsonify({"success": False, "message": "Customer not found."}), 404)

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

    except psycopg2.Error as error:

        db.rollback()

        return (jsonify({"success": False, "message": str(error)}), 500)

    finally:

        cursor.close()
        db.close()


# ============================================================
# SALES PAGE
# ============================================================


@app.route("/sales")
def sales():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("sales.html", full_name=full_name)


# ============================================================
# CREATE SALE
# ============================================================


@app.route("/api/sales", methods=["POST"])
def create_sale():

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    data = request.get_json()

    if not data:

        return (jsonify({"success": False, "message": "No sale data received."}), 400)

    customer_id = data.get("customer_id")

    total_amount = data.get("total_amount", 0)

    discount = data.get("discount", 0)

    final_amount = data.get("final_amount", 0)

    items = data.get("items", [])

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

        return (jsonify({"success": False, "message": "Invalid sale amount."}), 400)

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

        db = get_db_connection()

        cursor = db.cursor(cursor_factory=RealDictCursor)

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

                db.rollback()

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

                return (
                    jsonify({"success": False, "message": "Invalid sale item."}),
                    400,
                )

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

            return (
                jsonify({"success": False, "message": "Sale total is invalid."}),
                400,
            )

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
            (
                %s,
                %s,
                %s,
                %s
            )

            RETURNING id
            """,
            (customer_id, calculated_total, discount, calculated_final),
        )

        sale_id = cursor.fetchone()["id"]

        # ===============================
        # SALE ITEMS + STOCK
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
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    sale_id,
                    item["product_id"],
                    item["quantity"],
                    item["unit_price"],
                    item["subtotal"],
                ),
            )

            cursor.execute(
                """
                UPDATE products

                SET
                    stock_quantity =
                        stock_quantity - %s,
                    updated_at = NOW()

                WHERE id = %s
                """,
                (item["quantity"], item["product_id"]),
            )

        # ===============================
        # COMMIT
        # ===============================

        db.commit()

        # ===============================
        # CUSTOMER NAME
        # ===============================

        customer_name = "Walk-in Customer"

        if customer_id:

            cursor.execute(
                """
                SELECT customer_name
                FROM customers
                WHERE id = %s
                """,
                (customer_id,),
            )

            customer = cursor.fetchone()

            if customer:

                customer_name = customer["customer_name"]

        # ===============================
        # BUSINESS CURRENCY
        # ===============================

        currency = "PKR"

        cursor.execute("""
            SELECT currency
            FROM business_settings
            ORDER BY id ASC
            LIMIT 1
            """)

        business_settings = cursor.fetchone()

        if business_settings and business_settings["currency"]:

            currency = business_settings["currency"]

        # ===============================
        # INVOICE ITEMS
        # ===============================

        cursor.execute(
            """
            SELECT
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

        invoice_items = cursor.fetchall()

        # ===============================
        # GENERATE INVOICE
        # ===============================

        invoice_url = generate_invoice_image(
            sale_id=sale_id,
            customer_name=customer_name,
            items=invoice_items,
            subtotal=calculated_total,
            discount=discount,
            final_amount=calculated_final,
            currency=currency,
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Sale completed successfully.",
                    "sale_id": sale_id,
                    "invoice_url": invoice_url,
                }
            ),
            201,
        )

    except psycopg2.Error as error:

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


# ============================================================
# SALES HISTORY PAGE
# ============================================================


@app.route("/sales-history")
def sales_history():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("sales-history.html", full_name=full_name)


# ============================================================
# GET SALES HISTORY
# ============================================================


@app.route("/api/sales", methods=["GET"])
def get_sales():

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(cursor_factory=RealDictCursor)

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

        return jsonify(make_json_safe({"success": True, "sales": sales})), 200

    except psycopg2.Error as error:

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


# ============================================================
# GET SINGLE SALE DETAILS
# ============================================================


@app.route("/api/sales/<int:sale_id>", methods=["GET"])
def get_sale_details(sale_id):

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(cursor_factory=RealDictCursor)

        # SALE

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

            return (jsonify({"success": False, "message": "Sale not found."}), 404)

        # ITEMS

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

        return (
            jsonify(make_json_safe({"success": True, "sale": sale, "items": items})),
            200,
        )

    except psycopg2.Error as error:

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


# ============================================================
# SETTINGS PAGE
# ============================================================


@app.route("/settings")
def settings():

    if "user_id" not in session:
        return redirect(url_for("home"))

    full_name = session["username"]

    return render_template("settings.html", full_name=full_name)


# ============================================================
# SETTINGS - GET PROFILE
# ============================================================


@app.route("/api/settings/profile", methods=["GET"])
def get_settings_profile():

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(cursor_factory=RealDictCursor)

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

            return (jsonify({"success": False, "message": "User not found."}), 404)

        return jsonify(make_json_safe({"success": True, "user": user})), 200

    except psycopg2.Error as error:

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


# ============================================================
# SETTINGS - UPDATE PROFILE
# ============================================================


@app.route("/api/settings/profile", methods=["PUT"])
def update_settings_profile():

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    data = request.get_json()

    if not data:

        return (jsonify({"success": False, "message": "No data received."}), 400)

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

        cursor = db.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT id

            FROM users

            WHERE
                (
                    username = %s
                    OR email = %s
                )

                AND id != %s
            """,
            (username, email, session["user_id"]),
        )

        existing_user = cursor.fetchone()

        if existing_user:

            db.rollback()

            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Username or email is already in use.",
                    }
                ),
                409,
            )

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

        session["username"] = username

        return (
            jsonify({"success": True, "message": "Profile updated successfully."}),
            200,
        )

    except psycopg2.Error as error:

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


# ============================================================
# SETTINGS - CHANGE PASSWORD
# ============================================================


@app.route("/api/settings/password", methods=["PUT"])
def change_password():

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    data = request.get_json()

    if not data:

        return (jsonify({"success": False, "message": "No data received."}), 400)

    current_password = data.get("currentPassword", "")

    new_password = data.get("newPassword", "")

    confirm_password = data.get("confirmPassword", "")

    if not current_password or not new_password or not confirm_password:

        return (
            jsonify({"success": False, "message": "All password fields are required."}),
            400,
        )

    if new_password != confirm_password:

        return (
            jsonify({"success": False, "message": "New passwords do not match."}),
            400,
        )

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

        cursor = db.cursor(cursor_factory=RealDictCursor)

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

            return (jsonify({"success": False, "message": "User not found."}), 404)

        if not check_password_hash(user["password"], current_password):

            return (
                jsonify(
                    {"success": False, "message": "Current password is incorrect."}
                ),
                401,
            )

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

        new_password_hash = generate_password_hash(new_password)

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

    except psycopg2.Error as error:

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


# ============================================================
# SETTINGS - GET BUSINESS INFORMATION
# ============================================================


@app.route("/api/settings/business", methods=["GET"])
def get_business_settings():

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    db = None
    cursor = None

    try:

        db = get_db_connection()

        cursor = db.cursor(cursor_factory=RealDictCursor)

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

        return jsonify(make_json_safe({"success": True, "business": business})), 200

    except psycopg2.Error as error:

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


# ============================================================
# SETTINGS - UPDATE BUSINESS INFORMATION
# ============================================================


@app.route("/api/settings/business", methods=["PUT"])
def update_business_settings():

    if "user_id" not in session:

        return (jsonify({"success": False, "message": "Please login first."}), 401)

    data = request.get_json()

    if not data:

        return (jsonify({"success": False, "message": "No data received."}), 400)

    business_name = data.get("businessName", "").strip()

    business_phone = data.get("businessPhone", "").strip()

    business_email = data.get("businessEmail", "").strip()

    currency = data.get("currency", "PKR").strip()

    business_address = data.get("businessAddress", "").strip()

    if not business_name:

        return (
            jsonify({"success": False, "message": "Business name is required."}),
            400,
        )

    if business_email:

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

        cursor.execute("""
            SELECT id

            FROM business_settings

            ORDER BY id ASC

            LIMIT 1
            """)

        existing_settings = cursor.fetchone()

        if existing_settings:

            cursor.execute(
                """
                UPDATE business_settings

                SET
                    business_name = %s,
                    business_phone = %s,
                    business_email = %s,
                    currency = %s,
                    business_address = %s,
                    updated_at = NOW()

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

            cursor.execute(
                """
                INSERT INTO business_settings
                (
                    business_name,
                    business_phone,
                    business_email,
                    currency,
                    business_address
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
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

    except psycopg2.Error as error:

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


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
