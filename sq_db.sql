-- Основное меню (параметры фильтра)
CREATE TABLE IF NOT EXISTS mainmenu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_date DATE NOT NULL,
    second_date DATE NOT NULL,
    site1 TEXT NOT NULL,
    full_path BOOLEAN NOT NULL
);

-- GA
CREATE TABLE IF NOT EXISTS GA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_date DATE,
    site_path TEXT,
    advertising_site_id INTEGER,
    visit_count INTEGER,
    location TEXT,
    channel TEXT,
    site_id INTEGER -- ← добавляем
);

-- YM
CREATE TABLE IF NOT EXISTS YM (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_date DATE,
    site_path TEXT,
    advertising_site_id INTEGER,
    visit_count INTEGER,
    location TEXT,
    channel TEXT,
    site_id INTEGER -- ← добавляем
);

-- Продукты ERP
CREATE TABLE IF NOT EXISTS ERP_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    amount_money INTEGER,
    product_name TEXT,
    category TEXT
);

-- Покупатели ERP
CREATE TABLE IF NOT EXISTS ERP_buyer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_name TEXT NOT NULL,
    buyer_email TEXT,
    purchase_date DATE,
    product_id INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES ERP_products(id)
);
