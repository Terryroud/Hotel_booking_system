--Клиенты с наибольшими суммарными тратами

SELECT c.first_name, c.last_name, SUM(p.amount) AS total_spent
FROM CLIENTS c
JOIN BOOKINGS b ON c.client_id = b.client_id
JOIN PAYMENTS p ON b.booking_id = p.booking_id
GROUP BY c.client_id, c.first_name, c.last_name
HAVING SUM(p.amount) > (SELECT AVG(amount) FROM PAYMENTS) * 3
ORDER BY total_spent DESC;