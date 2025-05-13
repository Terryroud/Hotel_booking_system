-- представление с информацией о бронированиях и клиентах
create view booking_client_view as
select b.booking_id,
	   c.first_name || ' ' || c.last_name as client_name,
	   c.email as client_email,
	   b.check_in_date,
	   b.check_out_date,
       b.total_price,
	   b.status
from BOOKINGS b
join CLIENTS c on b.client_id = c.client_id;

-- представление с рейтингами отелей
create view hotel_rating_view as
select h.hotel_id,
	   h.name as hotel_name,
	   h.stars,
	   ROUND(AVG(r.rating), 1) as avg_rating,
	   COUNT(r.review_id) as review_count
from HOTELS h
left join REVIEWS r on h.hotel_id = r.hotel_id
group by h.hotel_id, h.name, h.stars;
