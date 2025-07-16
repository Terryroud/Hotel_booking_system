--Поиск самых популярных периодов бронирования (анализ дат)

SELECT 
    TO_CHAR(DATE_TRUNC('month', check_in_date), 'YYYY-MM') AS month,
    COUNT(*) AS bookings_count,
    ROUND(AVG(total_price), 2) AS avg_booking_price
FROM BOOKINGS
GROUP BY DATE_TRUNC('month', check_in_date)
ORDER BY bookings_count DESC
LIMIT 3;