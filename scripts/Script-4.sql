--Рейтинг отелей по категориям звезд: ранжирование отелей по средней оценке внутри группы отелей с одинаковым кол-вом звезд

SELECT
    h.name AS hotel_name,
    h.stars,
    ROUND(AVG(r.rating), 2) AS avg_rating,
    RANK() OVER (PARTITION BY h.stars ORDER BY AVG(r.rating) DESC) AS rank_in_category
FROM HOTELS h
LEFT JOIN REVIEWS r ON h.hotel_id = r.hotel_id
GROUP BY h.hotel_id
ORDER BY h.stars, avg_rating DESC;