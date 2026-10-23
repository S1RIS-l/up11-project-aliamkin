DROP DATABASE IF EXISTS formadessert;
CREATE DATABASE formadessert;
\c formadessert;

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
INSERT INTO roles (name) VALUES 
('Администратор'), ('Менеджер'), ('Клиент');

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
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE subcategories (
    subcategory_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(100) NOT NULL,
    UNIQUE (category_id, name)
);

CREATE TABLE manufacturers (
    manufacturer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE variants (
    variant_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE statuses (
    status_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    article VARCHAR(20) NOT NULL UNIQUE,
    category_id INTEGER REFERENCES categories(category_id),
    subcategory_id INTEGER REFERENCES subcategories(subcategory_id),
    manufacturer_id INTEGER REFERENCES manufacturers(manufacturer_id),
    name VARCHAR(200) NOT NULL,
    image VARCHAR(200),
    material VARCHAR(100),
    description TEXT,
    price NUMERIC(10,2) CHECK (price >= 0)
);

CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    variant_id INTEGER REFERENCES variants(variant_id),
    quantity INTEGER CHECK (quantity >= 0),
    UNIQUE (product_id, variant_id)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id INTEGER REFERENCES users(user_id),
    status_id INTEGER REFERENCES statuses(status_id)
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    stock_item_id INTEGER REFERENCES stock_items(stock_item_id),
    quantity INTEGER CHECK (quantity > 0),
    price NUMERIC(10,2) CHECK (unit_price >= 0)
);

1.7:
INSERT INTO categories (name) VALUES 
('Формы для выпечки'), ('Кондитерские лопатки'), ('Коврики'), 
('Кисти'), ('Кондитерские мешки'), ('Скребки');

INSERT INTO subcategories (category_id, name) VALUES 
(1, 'Стандартные'), (1, 'Профессиональные'),
(2, 'Стандартные'), (2, 'Профессиональные'),
(3, 'Стандартные'), (3, 'Профессиональные'),
(4, 'Стандартные'), (4, 'Профессиональные'),
(5, 'Стандартные'), (5, 'Профессиональные'),
(6, 'Стандартные'), (6, 'Профессиональные');

INSERT INTO manufacturers (name) VALUES 
('СиликоПроф'), ('КондитерЛайн'), ('ДесертФорм');

INSERT INTO variants (name) VALUES 
('Синий'), ('Красный');

INSERT INTO products (article, category_id, subcategory_id, manufacturer_id, name, image, material, description, price) VALUES 
('FD0001', 1, 1, 1, 'Форма силиконовая 101', 'Images/FD0001.png', 'Силикон', 'Форма силиконовая для приготовления и оформления десертов.', 750.00),
('FD0002', 2, 1, 2, 'Лопатка кондитерская 102', 'Images/FD0002.png', 'Силикон', 'Лопатка кондитерская для приготовления и оформления десертов.', 480.00),
('FD0003', 3, 1, 3, 'Коврик для теста 103', 'Images/FD0003.png', 'Силикон', 'Коврик для теста для приготовления и оформления десертов.', 1150.00),
('FD0004', 4, 1, 1, 'Кисть кулинарная 104', 'Images/FD0004.png', 'Силикон', 'Кисть кулинарная для приготовления и оформления десертов.', 620.00),
('FD0005', 5, 1, 2, 'Мешок кондитерский многоразовый 105', 'Images/FD0005.png', 'Силикон', 'Мешок кондитерский многоразовый для приготовления и оформления десертов.', 950.00);

1.8:
INSERT INTO users (login, last_name, first_name, middle_name, role_id) VALUES 
('admin', 'Миронов', 'Алексей', 'Игоревич', 1),
('manager', 'Лебедева', 'Мария', 'Олеговна', 2),
('client1', 'Соколов', 'Иван', 'Александрович', 3),
('client2', 'Кузнецова', 'Анна', 'Сергеевна', 3),
('client3', 'Волков', 'Денис', 'Александрович', 3),
('client4', 'Орлова', 'Елена', 'Сергеевна', 3),
('client5', 'Павлов', 'Олег', 'Александрович', 3),
('client6', 'Белова', 'Ирина', 'Сергеевна', 3);

1.9:
INSERT INTO statuses (name) VALUES ('Новый'), ('Подтверждён');

INSERT INTO stock_items (product_id, variant_id, quantity) VALUES 
(1, 1, 0), (1, 2, 0),
(2, 1, 1), (2, 2, 2),
(3, 1, 2), (3, 2, 2);

INSERT INTO orders (order_id, order_date, user_id, status_id) VALUES 
(1, '2026-09-01', 3, 2),
(2, '2026-09-02', 4, 1),
(3, '2026-09-03', 5, 2),
(4, '2026-09-04', 6, 1),
(5, '2026-09-05', 7, 2);

INSERT INTO order_items (order_id, stock_item_id, quantity, unit_price) VALUES 
(1, 10, 2, 950.00),
(2, 13, 1, 1350.00),
(3, 18, 2, 1750.00),
(3, 19, 1, 1220.00),
(4, 21, 1, 1550.00);
