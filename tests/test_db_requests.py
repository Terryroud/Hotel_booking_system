import pytest
import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("TEST_DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    yield conn
    conn.close()

# Тест 1. Топ-5 отелей по количеству бронирований
def test_top_hotels(db_connection):
    query = """
    SELECT h.name AS hotel_name, COUNT(b.booking_id) AS bookings_count
    FROM hotels h
    JOIN rooms r ON h.hotel_id = r.hotel_id
    JOIN bookings b ON r.room_id = b.room_id
    GROUP BY h.hotel_id, h.name
    ORDER BY bookings_count DESC
    LIMIT 5;
    """
    df = pd.read_sql(query, db_connection)
    assert len(df) == 5
    assert all(df['bookings_count'] > 0)

# Тест 2. Клиенты с наибольшими суммарными тратами
def test_top_clients_by_spending(db_connection):
    query = """
    SELECT c.first_name, c.last_name, SUM(p.amount) AS total_spent
    FROM clients c
    JOIN bookings b ON c.client_id = b.client_id
    JOIN payments p ON b.booking_id = p.booking_id
    GROUP BY c.client_id, c.first_name, c.last_name
    HAVING SUM(p.amount) > (SELECT AVG(amount) FROM payments) * 3
    ORDER BY total_spent DESC;
    """
    df = pd.read_sql(query, db_connection)
    avg_payment = pd.read_sql("SELECT AVG(amount) FROM payments", db_connection).iloc[0, 0]
    assert all(df['total_spent'] > avg_payment * 3)

# Тест 3. Свободные номера на конкретную дату
def test_available_rooms(db_connection):
    test_date = '2023-07-15'
    query = f"""
    SELECT r.room_id, h.name AS hotel_name, r.room_type, r.price
    FROM rooms r
    JOIN hotels h ON r.hotel_id = h.hotel_id
    WHERE NOT EXISTS (
        SELECT 1 FROM bookings b 
        WHERE b.room_id = r.room_id 
        AND '{test_date}' BETWEEN b.check_in_date AND b.check_out_date
    )
    ORDER BY r.price;
    """
    df = pd.read_sql(query, db_connection)
    if not df.empty:
        for room_id in df['room_id']:
            test_query = f"""
            SELECT 1 FROM bookings 
            WHERE room_id = {room_id}
            AND '{test_date}' BETWEEN check_in_date AND check_out_date
            LIMIT 1;
            """
            result = pd.read_sql(test_query, db_connection)
            assert result.empty

# Тест 4. Рейтинг отелей по категориям звезд: ранжирование отелей по средней оценке внутри группы отелей с одинаковым кол-вом звезд
def test_hotel_ratings_by_stars(db_connection):
    query = """
    SELECT
        h.name AS hotel_name,
        h.stars,
        ROUND(AVG(r.rating), 2) AS avg_rating,
        RANK() OVER (PARTITION BY h.stars ORDER BY AVG(r.rating) DESC) AS rank_in_category
    FROM hotels h
    LEFT JOIN reviews r ON h.hotel_id = r.hotel_id
    GROUP BY h.hotel_id
    ORDER BY h.stars, avg_rating DESC;
    """
    df = pd.read_sql(query, db_connection)
    for stars in df['stars'].unique():
        test_group = df[df['stars'] == stars]
        assert test_group['avg_rating'].is_monotonic_decreasing

# Тест 5. Поиск самых популярных периодов бронирования (анализ дат)
def test_popular_booking_periods(db_connection):
    query = """
    SELECT 
        TO_CHAR(DATE_TRUNC('month', check_in_date), 'YYYY-MM') AS month,
        COUNT(*) AS bookings_count,
        ROUND(AVG(total_price), 2) AS avg_booking_price
    FROM bookings
    GROUP BY DATE_TRUNC('month', check_in_date)
    ORDER BY bookings_count DESC
    LIMIT 3;
    """
    df = pd.read_sql(query, db_connection)
    assert len(df) <= 3
    assert all(df['bookings_count'] >= 0)

# Тест 6. Анализ отмененных бронирований
def test_cancelled_bookings_analysis(db_connection):
    query = """
    SELECT 
        h.name AS hotel_name,
        COUNT(*) FILTER (WHERE b.status = 'отменено') AS cancelled_bookings,
        COUNT(*) AS total_bookings,
        ROUND(COUNT(*) FILTER (WHERE b.status = 'отменено') * 100.0 / 
              NULLIF(COUNT(*), 0), 2) AS cancellation_rate
    FROM hotels h
    JOIN bookings b ON EXISTS (
        SELECT 1 FROM rooms r 
        WHERE r.hotel_id = h.hotel_id AND r.room_id = b.room_id
    )
    GROUP BY h.hotel_id, h.name
    ORDER BY cancellation_rate DESC;
    """
    df = pd.read_sql(query, db_connection)
    for i, row in df.iterrows():
        test_rate = (row['cancelled_bookings'] / row['total_bookings']) * 100
        assert abs(row['cancellation_rate'] - test_rate) < 0.001

# Тест 7. Вывод всех бронирований номеров типа Люкс
def test_lux_room_bookings(db_connection):
    query = """
    SELECT
        c.first_name || ' ' || c.last_name AS client_name,
        r.room_type,
        h.name AS hotel_name,
        (b.check_out_date - b.check_in_date) AS duration_days,
        b.total_price
    FROM bookings b
    JOIN rooms r ON b.room_id = r.room_id
    JOIN hotels h ON r.hotel_id = h.hotel_id
    JOIN clients c ON b.client_id = c.client_id
    WHERE LOWER(r.room_type) LIKE '%люкс%'
    ORDER BY duration_days DESC;
    """
    df = pd.read_sql(query, db_connection)
    if not df.empty:
        assert all(df['room_type'].str.contains('люкс', case=False))

# Тест 8. Вывод для каждого отеля средней продолжительности бронирований (в днях)
def test_avg_booking_duration(db_connection):
    query = """
    SELECT
        h.name AS hotel_name,
        ROUND(AVG(b.check_out_date - b.check_in_date), 2) AS avg_booking_period,
        COUNT(b.booking_id) AS total_bookings
    FROM hotels h
    JOIN rooms r ON h.hotel_id = r.hotel_id
    JOIN bookings b ON r.room_id = b.room_id
    GROUP BY h.hotel_id, h.name
    ORDER BY avg_booking_period DESC;
    """
    df = pd.read_sql(query, db_connection)
    assert all(df['avg_booking_period'] > 0)

# Тест 9. Соотношение цены номера и стоимости услуг в отеле
def test_price_ratio(db_connection):
    query = """
    SELECT 
        h.name AS hotel_name,
        AVG(hs.price) AS avg_service_price,
        AVG(r.price) AS avg_room_price,
        ROUND(AVG(hs.price) / NULLIF(AVG(r.price), 0), 2) AS service_to_room_price_ratio
    FROM hotels h
    JOIN hotel_services hs ON h.hotel_id = hs.hotel_id
    JOIN rooms r ON h.hotel_id = r.hotel_id
    GROUP BY h.hotel_id, h.name
    HAVING AVG(hs.price) > 0
    ORDER BY service_to_room_price_ratio DESC;
    """
    df = pd.read_sql(query, db_connection)
    for i, row in df.iterrows():
        test_ratio = row['avg_service_price'] / row['avg_room_price']
        assert abs(row['service_to_room_price_ratio'] - test_ratio) < 0.001

# Тест 10. Клиенты, которые бронировали отели с услугой spa
def test_spa_clients(db_connection):
    query = """
    SELECT 
        c.first_name || ' ' || c.last_name AS client_name,
        h.name AS hotel_name,
        hs.name AS service_available
    FROM clients c
    JOIN bookings b ON c.client_id = b.client_id
    JOIN rooms r ON b.room_id = r.room_id
    JOIN hotels h ON r.hotel_id = h.hotel_id
    JOIN hotel_services hs ON h.hotel_id = hs.hotel_id
    WHERE hs.name ILIKE '%spa%'
    ORDER BY c.last_name;
    """
    df = pd.read_sql(query, db_connection)
    if not df.empty:
        assert all(df['service_available'].str.contains('spa', case=False))

# Тест 11. Отели с рейтингом выше среднего
def test_above_average_hotels(db_connection):
    test_avg_rating = pd.read_sql("SELECT AVG(rating) FROM reviews", db_connection).iloc[0, 0]
    query = """
    SELECT h.name AS hotel_name, ROUND(AVG(r.rating), 2) AS avg_rating
    FROM hotels h
    JOIN reviews r ON h.hotel_id = r.hotel_id
    GROUP BY h.hotel_id, h.name
    HAVING AVG(r.rating) > (SELECT AVG(rating) FROM reviews)
    ORDER BY avg_rating DESC;
    """
    df = pd.read_sql(query, db_connection)
    if not df.empty:
        assert all(df['avg_rating'] > test_avg_rating)

# Тест 12. Проверка, что нет бронирований с некорректными датами
def test_booking_data_correct(db_connection):
    query = "SELECT COUNT(*) FROM bookings WHERE check_out_date <= check_in_date"
    result = pd.read_sql(query, db_connection).iloc[0, 0]
    assert result == 0
