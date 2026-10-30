DROP DATABASE IF EXISTS opticworld;
CREATE DATABASE opticworld;

\c opticworld;

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    login VARCHAR(100) NOT NULL UNIQUE,
    role_id INTEGER REFERENCES roles(role_id)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    UNIQUE (name, subcategory)
);

CREATE TABLE subcategories (
    subcategory_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(100) NOT NULL,
    UNIQUE (category_id, name)
);

CREATE TABLE variants (
    variant_id SERIAL PRIMARY KEY,
    value VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100),
    description TEXT,
    composition TEXT,
    price NUMERIC(10,2) CHECK (price > 0),
    image_path VARCHAR(255)
);

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    variant_id INTEGER REFERENCES variants(variant_id),
    quantity INTEGER CHECK (quantity >= 0),
    price NUMERIC(10,2) CHECK (price > 0),
    UNIQUE (product_id, variant_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id INTEGER REFERENCES users(user_id)
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    variant_id INTEGER REFERENCES variants(variant_id),
    quantity INTEGER CHECK (quantity > 0),
    price NUMERIC(10,2) CHECK (price > 0)
);