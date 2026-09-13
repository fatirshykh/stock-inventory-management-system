# Smart Inventory & Sales Management System (SIMS)

A full-stack web-based **Smart Inventory & Sales Management System (SIMS)** built with **Python Flask, MySQL, HTML, CSS, and JavaScript**.

SIMS is designed to help businesses manage their products, categories, inventory, customers, sales, and sales history through a simple and modern dashboard.

The project is currently being prepared for **online deployment**, allowing customers to access the system through a web browser without installing additional software.

---

## 📌 Project Overview

**SIMS — Smart Inventory & Sales Management System** is a complete business management application designed for small and medium-sized businesses.

The system provides a centralized platform for:

- User authentication
- Dashboard statistics
- Product management
- Category management
- Stock management
- Customer management
- Sales processing
- Sales history
- Business settings

The application uses a Flask backend to communicate with a MySQL database and JavaScript-based frontend functionality through REST-style APIs.

---

## ✨ Features

### 🔐 Authentication

- User registration
- User login
- Username or email login
- Password hashing
- Session-based authentication
- Protected application pages
- Logout functionality

### 📊 Dashboard

The dashboard provides an overview of the business, including:

- Total products
- Total categories
- Total customers
- Low-stock products
- Today's sales
- Recent sales
- Low-stock product list

Dashboard information is loaded dynamically from the MySQL database.

### 📦 Product Management

Users can:

- Add products
- Edit products
- Delete products
- View products
- Assign products to categories
- Set product prices
- Set stock quantities
- Set minimum stock levels
- Manage product SKUs

### 🗂️ Category Management

Users can:

- Add categories
- Edit categories
- Delete categories
- View categories
- Organize products by category

### 📈 Stock Management

The stock module provides:

- Stock In
- Stock Out
- Current stock quantity
- Minimum stock level
- Low-stock identification
- Automatic stock updates

Stock quantities are automatically affected when sales are completed.

### 👥 Customer Management

Users can:

- Add customers
- Edit customers
- Delete customers
- View customers
- Store customer contact information

### 🛒 New Sale

The sales module allows users to:

- Select a customer
- Select products
- Add multiple products to a sale
- Set quantities
- Automatically calculate subtotals
- Apply percentage discounts
- Calculate final amounts
- Validate available stock
- Complete sales

When a sale is completed, the system automatically:

1. Creates the sale record.
2. Creates the sale item records.
3. Deducts sold quantities from product stock.
4. Calculates the final amount.
5. Saves the transaction in MySQL.

### 🧾 Sales History

Users can:

- View previous sales
- Search sales
- View customer information
- View sale amounts
- View sale dates
- View sale details
- View individual sale items

### ⚙️ Settings

The settings module provides:

- Profile information
- Password management
- Business information
- Currency settings
- Business address
- System information

---

# 🛠️ Technologies Used

## Frontend

- HTML5
- CSS3
- JavaScript
- Fetch API
- Responsive CSS

## Backend

- Python
- Flask
- Flask Sessions
- REST-style API routes

## Database

- MySQL
- MySQL Connector/Python

## Security

- Werkzeug password hashing
- Environment variables
- Session-based authentication
- Protected API routes
- Server-side validation

## Development Tools

- Visual Studio Code
- XAMPP
- MySQL
- Git
- GitHub

---

# 🏗️ Application Architecture

SIMS follows a simple full-stack architecture:

```text
┌──────────────────────────┐
│        Frontend          │
│                          │
│ HTML / CSS / JavaScript  │
└────────────┬─────────────┘
             │
             │ HTTP / Fetch API
             ▼
┌──────────────────────────┐
│       Flask Backend      │
│                          │
│ Routes / APIs / Sessions │
│ Business Logic           │
└────────────┬─────────────┘
             │
             │ MySQL Connector
             ▼
┌──────────────────────────┐
│       MySQL Database     │
│                          │
│ Users                    │
│ Categories               │
│ Products                 │
│ Customers                │
│ Sales                    │
│ Sale Items               │
└──────────────────────────┘
```

---

# 📁 Project Structure

```text
SIMS/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .env
├── .env.example
├── .gitignore
│
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── products.html
│   ├── categories.html
│   ├── stock.html
│   ├── customers.html
│   ├── sales.html
│   ├── sales-history.html
│   └── settings.html
│
└── static/
    │
    ├── css/
    │   └── style.css
    │
    └── js/
        ├── dashboard.js
        ├── products.js
        ├── categories.js
        ├── stock.js
        ├── customers.js
        ├── sales.js
        ├── sales-history.js
        └── settings.js
```

> The final project structure may change as the application is prepared for production deployment.

---

# 🗄️ Database Structure

SIMS uses MySQL as its primary database.

## Users

Stores application user accounts.

```text
users
├── id
├── full_name
├── username
├── email
├── phone
└── password
```

## Categories

Stores product categories.

```text
categories
├── id
└── name
```

## Products

Stores product information and inventory quantities.

```text
products
├── id
├── category_id
├── product_name
├── sku
├── price
├── stock_quantity
└── minimum_stock
```

## Customers

Stores customer information.

```text
customers
├── id
├── customer_name
├── phone
├── email
└── address
```

## Sales

Stores the main sale transaction.

```text
sales
├── id
├── customer_id
├── total_amount
├── discount
├── final_amount
└── created_at
```

## Sale Items

Stores individual products included in each sale.

```text
sale_items
├── id
├── sale_id
├── product_id
├── quantity
├── unit_price
└── subtotal
```

---

# 🔗 Database Relationships

The main relationships are:

```text
Categories
     │
     └────── Products


Customers
     │
     └────── Sales
                │
                └────── Sale Items
                            │
                            └────── Products
```

### Sales Relationship

One customer can have multiple sales.

```text
Customer
   │
   ├── Sale #1
   ├── Sale #2
   └── Sale #3
```

### Sale Items Relationship

One sale can contain multiple products.

```text
Sale
 │
 ├── Product A × 2
 ├── Product B × 1
 └── Product C × 5
```

---

# 💰 Sales Calculation

SIMS calculates sales using the following logic:

```text
Subtotal = Sum of all item subtotals

Discount Amount =
Subtotal × (Discount Percentage / 100)

Final Amount =
Subtotal - Discount Amount
```

Example:

```text
Subtotal = 10,000

Discount = 10%

Discount Amount = 1,000

Final Amount = 9,000
```

---

# 📦 Stock Logic

When a sale is completed:

```text
Current Stock
      ↓
Check Available Quantity
      ↓
Validate Requested Quantity
      ↓
Create Sale
      ↓
Create Sale Items
      ↓
Deduct Sold Quantity
      ↓
Update Product Stock
```

The backend verifies stock availability before completing a transaction.

This prevents users from selling more products than are currently available.

---

# 🔒 Security

The application includes several security practices:

- Password hashing using Werkzeug
- Session-based authentication
- Protected routes
- Protected APIs
- Server-side validation
- Database transactions for sales
- Database rollback when transaction errors occur
- Environment variables for sensitive configuration
- `.env` excluded from Git
- Database credentials not hardcoded in the repository

Sensitive values such as:

```text
SECRET_KEY
DB_HOST
DB_USER
DB_PASSWORD
DB_NAME
```

are intended to be provided through environment variables.

---

# ⚙️ Environment Configuration

Create a `.env` file locally:

```env
SECRET_KEY=your_secret_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=stock_management
```

Do not commit `.env` to GitHub.

Instead, provide a `.env.example` file:

```env
SECRET_KEY=your_secret_key_here

DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
```

---

# 📦 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/fatirshykh/stock-inventory-management-system.git
```

Enter the project directory:

```bash
cd stock-inventory-management-system
```

---

## 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure MySQL

Start MySQL using XAMPP or another MySQL server.

Create the database:

```sql
CREATE DATABASE stock_management;
```

Import the required SIMS database tables.

---

## 5. Configure Environment Variables

Create:

```text
.env
```

and add:

```env
SECRET_KEY=your_secret_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=stock_management
```

---

## 6. Run the Application

```bash
python app.py
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

---

# 🔄 Application Workflow

The main application workflow is:

```text
Signup
   ↓
Login
   ↓
Dashboard
   ↓
Products
   ↓
Categories
   ↓
Stock
   ↓
Customers
   ↓
New Sale
   ↓
Sales History
   ↓
Settings
```

---

# 📊 Dashboard Data

The dashboard obtains its data from the backend API:

```text
GET /api/dashboard/stats
```

The API provides:

- Total products
- Total categories
- Total customers
- Low stock count
- Today's sales
- Recent sales
- Low-stock products

---

# 🔌 Main API Endpoints

The application contains API endpoints for the main modules.

Examples include:

```text
POST   /signup
POST   /login

GET    /api/categories
POST   /api/categories
PUT    /api/categories/<id>
DELETE /api/categories/<id>

GET    /api/products
POST   /api/products
PUT    /api/products/<id>
DELETE /api/products/<id>

GET    /api/customers
POST   /api/customers
PUT    /api/customers/<id>
DELETE /api/customers/<id>

POST   /api/stock/in
POST   /api/stock/out

POST   /api/sales
GET    /api/sales
GET    /api/sales/<sale_id>

GET    /api/dashboard/stats

GET    /api/settings/profile
PUT    /api/settings/profile

GET    /api/settings/business
PUT    /api/settings/business

PUT    /api/settings/password
```

The exact endpoint list may expand as the project develops.

---

# 📱 Responsive Design

SIMS is designed to work across different screen sizes.

Supported interfaces include:

- Desktop
- Laptop
- Tablet
- Mobile devices

The dashboard-style interface uses:

- Responsive sidebar
- Mobile navigation
- Responsive tables
- Responsive cards
- Responsive forms
- Mobile-friendly layouts

---

# 🎨 UI Design

SIMS uses a modern dark dashboard interface.

The primary design includes:

- Dark background
- Red accent color
- Sidebar navigation
- Dashboard cards
- Tables
- Forms
- Modals
- Responsive layouts

The project is being consolidated around a shared global stylesheet:

```text
static/css/style.css
```

This allows all application pages to maintain a consistent design.

---

# 🧪 Testing

Before production deployment, the following workflows should be tested:

### Authentication

```text
Signup → Login → Dashboard → Logout
```

### Products

```text
Create → Read → Update → Delete
```

### Categories

```text
Create → Read → Update → Delete
```

### Stock

```text
Stock In → Check Stock → Stock Out
```

### Customers

```text
Create → Read → Update → Delete
```

### Sales

```text
Select Customer
      ↓
Select Product
      ↓
Set Quantity
      ↓
Calculate Total
      ↓
Apply Discount
      ↓
Complete Sale
      ↓
Deduct Stock
      ↓
Save Sale
```

### Dashboard

```text
Create Data
     ↓
Dashboard API
     ↓
Updated Statistics
```

---

# 🚀 Deployment

SIMS is being prepared for online deployment.

The planned production architecture is:

```text
Customer Browser
       │
       ▼
    Internet
       │
       ▼
 Flask Application
       │
       ▼
 Online MySQL
```

The application will eventually be accessible through a public web URL without requiring the customer to install Python, Flask, XAMPP, or MySQL.

A custom domain is optional and can be added later.

---

# 🔮 Future Improvements

Possible future features include:

- Multi-business support
- Role-based access control
- Admin and staff accounts
- Advanced reporting
- Sales reports
- Profit and loss reports
- Inventory reports
- PDF invoices
- Printable receipts
- Product search and filtering
- Advanced analytics
- Automatic database backups
- Email notifications
- WhatsApp integration
- Online deployment
- Cloud database
- API improvements
- Desktop application version
- Mobile application
- SaaS subscription system

---

# 📈 Product Vision

SIMS is being developed with the goal of becoming a practical business management platform that can be provided to multiple businesses.

The long-term architecture can support:

```text
                    SIMS
                     │
        ┌────────────┴────────────┐
        │                         │
    Business A                Business B
        │                         │
     Products                  Products
     Customers                 Customers
     Stock                     Stock
     Sales                     Sales
```

Each business should have isolated data and secure access.

---

# 👨‍💻 Developer

**Fatir Sheikh**

Full Stack Developer & AI Automation Engineer

BS Data Science Student
GIFT University, Gujranwala, Pakistan

---

# 📂 Repository

GitHub:

https://github.com/fatirshykh/stock-inventory-management-system

---

# 📄 License

This project is currently developed as a private/commercial software project.

All rights reserved unless otherwise specified.

---

# ⭐ Project Status

**Current Status: Active Development**

Core modules currently include:

- Authentication
- Dashboard
- Products
- Categories
- Stock
- Customers
- New Sale
- Sales History
- Settings

The next major phase is:

**Production deployment and online customer access.**

---

## SIMS

**Smart Inventory & Sales Management System**

> Manage Products. Track Stock. Manage Customers. Record Sales.
