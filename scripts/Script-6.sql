--Анализ отмененных бронирований

SELECT 
    h.name AS hotel_name,
    COUNT(*) FILTER (WHERE b.status = 'отменено') AS cancelled_bookings,
    COUNT(*) AS total_bookings,
    ROUND(COUNT(*) FILTER (WHERE b.status = 'отменено') * 100.0 / 
          NULLIF(COUNT(*), 0), 2) AS cancellation_rate
FROM HOTELS h
JOIN BOOKINGS b ON EXISTS (
    SELECT 1 FROM ROOMS r 
    WHERE r.hotel_id = h.hotel_id AND r.room_id = b.room_id
)
GROUP BY h.hotel_id, h.name
ORDER BY cancellation_rate DESC;