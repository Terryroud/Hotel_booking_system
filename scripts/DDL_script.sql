DROP TABLE IF EXISTS HOTEL_SERVICES;
DROP TABLE IF EXISTS ROOM_STATUS_HISTORY;
DROP TABLE IF EXISTS PAYMENTS;
DROP TABLE IF EXISTS REVIEWS;
DROP TABLE IF EXISTS BOOKINGS;
DROP TABLE IF EXISTS ROOMS;
DROP TABLE IF EXISTS CLIENTS;
DROP TABLE IF EXISTS HOTELS;
DROP TYPE IF EXISTS booking_status;
DROP TYPE IF EXISTS room_status;

-- Создание таблицы отелей
CREATE TABLE HOTELS (
    hotel_id INT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    stars INT CHECK (stars BETWEEN 1 AND 5),
    city VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL
);

COPY HOTELS FROM '/var/lib/postgresql/16/main/db_project_data/hotels.csv' WITH (FORMAT csv, HEADER true);

-- Создание таблицы клиентов
CREATE TABLE CLIENTS (
    client_id INT PRIMARY KEY,
    first_name VARCHAR(200) NOT NULL,
    last_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL
);

COPY CLIENTS FROM '/var/lib/postgresql/16/main/db_project_data/clients.csv' WITH (FORMAT csv, HEADER true);

-- Создание таблицы номеров
CREATE TABLE ROOMS (
    room_id INT PRIMARY KEY,
    hotel_id INT NOT NULL,
    room_type VARCHAR(200),
    price INT NOT NULL,
    capacity INT NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES HOTELS(hotel_id) ON DELETE CASCADE,
    CHECK (price > 0),
    CHECK (capacity > 0)
);

COPY ROOMS FROM '/var/lib/postgresql/16/main/db_project_data/rooms.csv' WITH (FORMAT csv, HEADER true);

-- создаем тип ENUM
CREATE TYPE booking_status AS ENUM('подтверждено', 'отменено', 'завершено');

-- Создание таблицы бронирований
CREATE TABLE BOOKINGS (
    booking_id INT PRIMARY KEY,
    client_id INT NOT NULL,
    room_id INT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    total_price INT NOT NULL,
    status booking_status DEFAULT 'подтверждено',
    FOREIGN KEY (client_id) REFERENCES CLIENTS(client_id),
    FOREIGN KEY (room_id) REFERENCES ROOMS(room_id),
    CHECK (check_out_date > check_in_date),
    CHECK (total_price > 0)
);

COPY BOOKINGS FROM '/var/lib/postgresql/16/main/db_project_data/bookings.csv' WITH (FORMAT csv, HEADER true);

-- Создание таблицы платежей
CREATE TABLE PAYMENTS (
    payment_id INT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount INT NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (booking_id) REFERENCES BOOKINGS(booking_id) ON DELETE CASCADE,
    CHECK (amount > 0)
);

COPY PAYMENTS FROM '/var/lib/postgresql/16/main/db_project_data/payments.csv' WITH (FORMAT csv, HEADER true);

-- Создание таблицы отзывов
CREATE TABLE REVIEWS (
    review_id INT PRIMARY KEY,
    hotel_id INT NOT NULL,
    client_id INT NOT NULL,
    rating INT NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (hotel_id) REFERENCES HOTELS(hotel_id) ON DELETE CASCADE,
    FOREIGN KEY (client_id) REFERENCES CLIENTS(client_id),
    CHECK (rating BETWEEN 1 AND 5)
);

COPY REVIEWS FROM '/var/lib/postgresql/16/main/db_project_data/reviews.csv' WITH (FORMAT csv, HEADER true);

-- Создание связующей таблицы услуг отеля
CREATE TABLE HOTEL_SERVICES (
    service_id INT PRIMARY KEY,
    hotel_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    price INT NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES HOTELS(hotel_id) ON DELETE CASCADE
);

COPY HOTEL_SERVICES FROM '/var/lib/postgresql/16/main/db_project_data/hotel_services.csv' WITH (FORMAT csv, HEADER true);

-- создаем тип ENUM
CREATE TYPE room_status AS ENUM('свободен', 'занят');

-- Создание таблицы истории цен (SCD Type 2)
CREATE TABLE ROOM_STATUS_HISTORY (
    history_id INT PRIMARY KEY,
    room_id INT NOT NULL,
    status room_status DEFAULT 'свободен',
    valid_from DATE NOT NULL,
    valid_to DATE,
    FOREIGN KEY (room_id) REFERENCES ROOMS(room_id) ON DELETE CASCADE,
    CHECK (valid_to IS NULL OR valid_to > valid_from)
);

COPY ROOM_STATUS_HISTORY FROM '/var/lib/postgresql/16/main/db_project_data/room_status_history.csv' WITH (FORMAT csv, HEADER true, NULL 'NULL');

