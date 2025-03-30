--Отели с рейтингом выше среднего

SELECT h.name AS hotel_name, ROUND(AVG(r.rating), 2) AS avg_rating
FROM HOTELS h
JOIN REVIEWS r ON h.hotel_id = r.hotel_id
GROUP BY h.hotel_id, h.name
HAVING AVG(r.rating) > (SELECT AVG(rating) FROM REVIEWS)
ORDER BY avg_rating DESC;