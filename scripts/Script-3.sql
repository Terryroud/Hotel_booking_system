--Свободные номера на конкретную дату

SELECT r.room_id, h.name AS hotel_name, r.room_type, r.price
FROM ROOMS r
JOIN HOTELS h ON r.hotel_id = h.hotel_id
WHERE NOT EXISTS (
    SELECT 1 FROM BOOKINGS b 
    WHERE b.room_id = r.room_id 
    AND '2023-07-15' BETWEEN b.check_in_date AND b.check_out_date
)
ORDER BY r.price;