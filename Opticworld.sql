-- =============================================
-- Скрипт создания БД «Мир оптики» (Тема 16)
-- =============================================

-- 1. Создание БД
CREATE DATABASE opticworld1;

-- Переключаемся на созданную базу
\c opticworld1;

-- 2. Справочники
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);
INSERT INTO roles (name) VALUES 
('Администратор'), ('Менеджер'), ('Авторизованный пользователь');

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    login VARCHAR(100) NOT NULL UNIQUE,
    role_id INTEGER REFERENCES roles(role_id)
);

INSERT INTO users (last_name, first_name, middle_name, login, role_id) VALUES 
('Иванов', 'Иван', 'Сергеевич', 'admin', 1),
('Петров', 'Пётр', 'Алексеевич', 'manager1', 2),
('Смирнова', 'Ольга', 'Викторовна', 'manager2', 2),
('Сидоров', 'Алексей', 'Иванович', 'client01', 3),
('Кузнецова', 'Анна', 'Ивановна', 'client02', 3);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);
INSERT INTO categories (name) VALUES 
('Оправы'), ('Солнцезащитные очки'), ('Аксессуары');

CREATE TABLE subcategories (
    subcategory_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    name VARCHAR(100) NOT NULL,
    UNIQUE (category_id, name)
);
INSERT INTO subcategories (category_id, name) VALUES 
(1, 'Металлические'), (1, 'Пластиковые'),
(2, 'Готовые изделия'), (3, 'Футляры');

CREATE TABLE variants (
    variant_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
INSERT INTO variants (name) VALUES 
('Чёрный'), ('Серый'), ('Коричневый');

-- 3. Товары
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    subcategory_id INTEGER REFERENCES subcategories(subcategory_id),
    name VARCHAR(200) NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    image VARCHAR(100),
    description TEXT,
    composition TEXT,
    base_price NUMERIC(10,2) CHECK (base_price > 0),
    UNIQUE (name, manufacturer)
);

INSERT INTO products (category_id, subcategory_id, name, manufacturer, image, description, composition, base_price) VALUES 
(1, 1, 'Оправа Круг', 'Ясный взгляд', 'IMG_16_001.png', 'Оправа Круг. Категория: Оправы. Тип: Металлические.', 'Металлическая оправа; демонстрационные вставки без оптической силы', 1990),
(1, 1, 'Оправа Овал', 'Фокус', 'IMG_16_002.png', 'Оправа Овал. Категория: Оправы. Тип: Металлические.', 'Металлическая оправа; демонстрационные вставки без оптической силы', 2290),
(1, 1, 'Оправа Линия', 'Линза', 'IMG_16_003.png', 'Оправа Линия. Категория: Оправы. Тип: Металлические.', 'Металлическая оправа; демонстрационные вставки без оптической силы', 2590),
(2, 3, 'Очки Солнце', 'Ясный взгляд', 'IMG_16_017.png', 'Очки Солнце. Категория: Солнцезащитные очки. Тип: Готовые изделия.', 'Полимерная оправа; тонированные линзы без коррекции зрения', 1290),
(3, 4, 'Футляр Линия', 'Линза', NULL, 'Футляр Линия. Категория: Аксессуары. Тип: Футляры.', 'Полимерный корпус; текстильная подкладка', 750);

-- 4. Товарные позиции
CREATE TABLE stock_items (
    stock_item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    variant_id INTEGER REFERENCES variants(variant_id),
    quantity INTEGER CHECK (quantity >= 0),
    price NUMERIC(10,2) CHECK (price > 0),
    UNIQUE (product_id, variant_id)
);

INSERT INTO stock_items (product_id, variant_id, quantity, price) VALUES 
(1, 1, 24, 1990), (1, 2, 5, 1990), (1, 3, 10, 1990),
(2, 1, 27, 2290), (2, 2, 8, 2290), (2, 3, 13, 2290);

-- 5. Заказы
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE,
    user_id INTEGER REFERENCES users(user_id)
);

INSERT INTO orders (order_id, order_date, user_id) VALUES 
(1, '2026-04-04', 4),
(2, '2026-04-06', 5),
(3, '2026-04-08', 1),
(4, '2026-04-10', 2),
(5, '2026-04-12', 3); 

-- 6. Состав заказов
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    stock_item_id INTEGER REFERENCES stock_items(stock_item_id),
    quantity INTEGER CHECK (quantity > 0),
    price NUMERIC(10,2) CHECK (price > 0)
);

INSERT INTO order_items (order_id, stock_item_id, quantity, price) VALUES 
(1, 1, 2, 1990),
(1, 4, 1, 2290),
(2, 2, 1, 2590),
(2, 5, 2, 2890);