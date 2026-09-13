CREATE DATABASE stock_management;

USE stock_management;

CREATE TABLE
    users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        fullname VARCHAR(100) NOT NULL,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        phone VARCHAR(20) NOT NULL,
        password VARCHAR(500) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    );

CREATE TABLE
    categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        status ENUM ('active', 'inactive') DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

CREATE TABLE
    products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        product_name VARCHAR(150) NOT NULL,
        sku VARCHAR(100) NOT NULL UNIQUE,
        category_id INT NOT NULL,
        purchase_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        selling_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        stock_quantity INT NOT NULL DEFAULT 0,
        minimum_stock INT NOT NULL DEFAULT 5,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT ON UPDATE CASCADE
    );

CREATE TABLE
    customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_name VARCHAR(150) NOT NULL,
        phone VARCHAR(30),
        email VARCHAR(150),
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );

CREATE TABLE
    sales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT NULL,
        total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        final_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE SET NULL
    );

CREATE TABLE
    sale_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sale_id INT NOT NULL,
        product_id INT NOT NULL,
        quantity INT NOT NULL,
        unit_price DECIMAL(10, 2) NOT NULL,
        subtotal DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT
    );

CREATE TABLE
    business_settings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        business_name VARCHAR(150) NOT NULL,
        business_phone VARCHAR(30),
        business_email VARCHAR(150),
        currency VARCHAR(10) NOT NULL DEFAULT 'PKR',
        business_address TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );