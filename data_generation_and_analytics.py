import os
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from faker import Faker
import random
from datetime import timedelta
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

load_dotenv()

# Функция подключения к базе данных
def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("TEST_DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    return conn

# Генерация данных в таблицу CLIENTS
def generate_clients(conn, start_id=401, end_id=600):
    fake = Faker('ru_RU')
    with conn.cursor() as cur:
        for client_id in range(start_id, end_id + 1):
            cur.execute(
                "insert into CLIENTS (client_id, first_name, last_name, email) values (%s, %s, %s, %s)",
                (client_id, fake.first_name(), fake.last_name(), fake.email())
            )
    conn.commit()

# Генерация данных в таблицу BOOKINGS
def generate_bookings(conn, start_id=800, end_id=1200):
    fake = Faker('ru_RU')
    with conn.cursor() as cur:
        cur.execute("select room_id from ROOMS")
        room_ids = [r[0] for r in cur.fetchall()]

        for booking_id in range(start_id, end_id + 1):
            room_id = random.choice(room_ids)
            client_id = random.randint(401, 600)
            check_in = fake.date_between(start_date='-1y', end_date='+1y')
            check_out = check_in + timedelta(days=random.randint(1, 21))
            price = random.randint(1000, 100000)
            status = random.choices(['подтверждено', 'отменено', 'завершено'], weights=[0.5, 0.1, 0.4])[0]

            cur.execute(
                """insert into BOOKINGS (booking_id, client_id, room_id, check_in_date, check_out_date, total_price, status) 
                   values (%s, %s, %s, %s, %s, %s, %s)""",
                (booking_id, client_id, room_id, check_in, check_out, price, status)
            )
    conn.commit()

# Основная функция генерации данных
def generate_data():
    conn = get_db_connection()
    try:
        generate_clients(conn)
        generate_bookings(conn)
        print("Done!")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()

# Загрузка данных о бронированиях
def load_bookings_data(conn):
    return pd.read_sql("""
        select b.*, h.stars, r.room_type, r.price as room_price
        from BOOKINGS b
        join ROOMS r on b.room_id = r.room_id
        join HOTELS h on r.hotel_id = h.hotel_id
    """, conn)

# Загрузка данных об отзывах
def load_reviews_data(conn):
    return pd.read_sql("""
        select r.rating, h.stars, h.city
        from REVIEWS r
        join HOTELS h on r.hotel_id = h.hotel_id
    """, conn)

# Построение зависимости рейтинга от количества звезд
def plot_rating_by_stars(reviews_df):
    plt.figure(figsize=(10, 6))
    reviews_df.boxplot(column='rating', by='stars')
    plt.title('Зависимость рейтинга от количества звезд')
    plt.xlabel('Количество звезд')
    plt.ylabel('Рейтинг')
    plt.savefig('rating_by_stars.png')
    plt.close()

# построение зависимости процента отмен от цены номера
def plot_cancellations_by_price(bookings_df):
    bookings_df['is_cancelled'] = (bookings_df['status'] == 'отменено')
    price_bins = pd.cut(bookings_df['room_price'], bins=5)
    price_groups = bookings_df.groupby(price_bins, observed=False)['is_cancelled'].agg(['mean', 'count'])

    plt.figure(figsize=(12, 8))
    ax = price_groups['mean'].mul(100).plot(kind='bar', width=0.85,alpha=0.8)

    for i, (val, count) in enumerate(zip(price_groups['mean'], price_groups['count'])):
        ax.text(i, val * 100 + 1, f'{val * 100:.1f}%\n(n={count})', ha='center', va='bottom', fontsize=10)

    plt.title('Процент отмен в зависимости от цены номера', pad=20, fontsize=14)
    plt.xlabel('Диапазон цены номера', fontsize=12)
    plt.ylabel('Процент отмен (%)', fontsize=12)

    labels = [f"{int(i.left)}-{int(i.right)} руб." for i in price_groups.index]
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
    plt.ylim(0, min(100, price_groups['mean'].max() * 100 + 15))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('cancel_by_price.png')
    plt.close()

# Визуализация сезонности бронирований
def plot_monthly_bookings(bookings_df):
    bookings_df['check_in_date'] = pd.to_datetime(bookings_df['check_in_date'])
    bookings_df['check_out_date'] = pd.to_datetime(bookings_df['check_out_date'])
    bookings_df['month'] = bookings_df['check_in_date'].dt.month
    monthly_bookings = bookings_df[bookings_df['status'] == 'подтверждено'].groupby('month').size()
    plt.figure(figsize=(10, 6))
    monthly_bookings.plot(kind='line', marker='o')
    plt.title('Количество бронирований по месяцам')
    plt.xlabel('Месяц')
    plt.ylabel('Количество бронирований')
    plt.xticks(range(1, 13))
    plt.grid()
    plt.savefig('bookings_by_month.png')
    plt.close()

# Основная функция анализа данных
def analyze_data():
    conn = get_db_connection()
    try:
        bookings_df = load_bookings_data(conn)
        reviews_df = load_reviews_data(conn)

        plot_rating_by_stars(reviews_df)
        plot_cancellations_by_price(bookings_df)
        plot_monthly_bookings(bookings_df)

        print("\nГрафики успешно сформированы!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    generate_data()
    analyze_data()