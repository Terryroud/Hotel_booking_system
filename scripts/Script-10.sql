--Клиенты, которые бронировали отели с услугой spa

SELECT 
    c.first_name || ' ' || c.last_name AS client_name,
    h.name AS hotel_name,
    hs.name AS service_available
FROM CLIENTS c
JOIN BOOKINGS b ON c.client_id = b.client_id
JOIN ROOMS r ON b.room_id = r.room_id
JOIN HOTELS h ON r.hotel_id = h.hotel_id
JOIN HOTEL_SERVICES hs ON h.hotel_id = hs.hotel_id
WHERE hs.name ILIKE '%spa%'
ORDER BY c.last_name;