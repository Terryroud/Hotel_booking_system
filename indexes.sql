-- индекс для поиска бронирований по датам
create index idx_bookings_dates on BOOKINGS(check_in_date, check_out_date);

-- индекс для поиска отзывов по отелю и рейтингу
create index idx_reviews_hotel_rating on REVIEWS(hotel_id, rating);

-- индекс для поиска номеров по типу и цене
create index idx_rooms_type_price on ROOMS(room_type, price);