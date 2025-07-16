-- Вывод всех бронирований номеров типа Люкс

SELECT
    c.first_name || ' ' || c.last_name AS client_name,
    r.room_type,
    h.name AS hotel_name,
    (b.check_out_date - b.check_in_date) AS duration_days,
    b.total_price
FROM BOOKINGS b
JOIN ROOMS r ON b.room_id = r.room_id
JOIN HOTELS h ON r.hotel_id = h.hotel_id
JOIN CLIENTS c ON b.client_id = c.client_id
WHERE LOWER(r.room_type) LIKE '%люкс%'
ORDER BY duration_days DESC;