-- Соотношение цены номера и стоимости услуг в отеле

SELECT 
    h.name AS hotel_name,
    AVG(hs.price) AS avg_service_price,
    AVG(r.price) AS avg_room_price,
    ROUND(AVG(hs.price) / NULLIF(AVG(r.price), 0), 2) AS service_to_room_price_ratio
FROM HOTELS h
JOIN HOTEL_SERVICES hs ON h.hotel_id = hs.hotel_id
JOIN ROOMS r ON h.hotel_id = r.hotel_id
GROUP BY h.hotel_id, h.name
HAVING AVG(hs.price) > 0
ORDER BY service_to_room_price_ratio DESC;