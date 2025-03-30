-- Топ-5 отелей по количеству бронирований

SELECT h.name AS hotel_name, COUNT(b.booking_id) AS bookings_count
FROM HOTELS h
JOIN ROOMS r ON h.hotel_id = r.hotel_id
JOIN BOOKINGS b ON r.room_id = b.room_id
GROUP BY h.hotel_id, h.name
ORDER BY bookings_count DESC
LIMIT 5;