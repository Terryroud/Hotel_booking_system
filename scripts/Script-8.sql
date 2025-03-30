--Вывод для каждого отеля средней продолжительности бронирований (в днях)

SELECT
    h.name AS hotel_name,
    ROUND(AVG(b.check_out_date - b.check_in_date), 2) AS avg_booking_period,
    COUNT(b.booking_id) AS total_bookings
FROM HOTELS h
JOIN ROOMS r ON h.hotel_id = r.hotel_id
JOIN BOOKINGS b ON r.room_id = b.room_id
GROUP BY h.hotel_id, h.name
ORDER BY avg_booking_period DESC;