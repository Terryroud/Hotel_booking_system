-- процедура отмены бронирования
create or replace procedure cancel_booking(cancel_booking_id int)
as $$
begin
    update BOOKINGS set status = 'отменено' 
    where booking_id = cancel_booking_id;
    raise notice 'Бронирование % отменено', cancel_booking_id;
end;
$$ language plpgsql;

-- процедура добавления нового клиента
create or replace procedure add_client(
	new_client_id int,
    new_first_name varchar,
    new_last_name varchar,
    new_email varchar)
as $$
begin
    insert into CLIENTS (client_id, first_name, last_name, email)
    values (new_client_id, new_first_name, new_last_name, new_email);
    raise notice 'Новый клиент успешно добавлен';
end;
$$ language plpgsql;

-- функция проверки доступности номера
create or replace function is_room_available(
    curr_room_id int,
    curr_check_in date,
    curr_check_out date)
returns boolean as $$
begin
    return not exists (
        select booking_id
        from BOOKINGS 
        where room_id = curr_room_id and status != 'отменено'
        and check_in_date < curr_check_out and check_out_date > curr_check_in);
end;
$$ language plpgsql;

-- функция подсчета количества бронирований клиента
create or replace function count_client_bookings(curr_client_id int)
returns int as $$
declare booking_count int;
begin
    select COUNT(*) into booking_count
    from BOOKINGS
    where client_id = curr_client_id;
    return booking_count;
end;
$$ language plpgsql;


