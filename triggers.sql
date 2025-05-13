-- проверка дат бронирования
create or replace function valid_booking_dates()
returns trigger as $$
begin
    if new.check_out_date <= new.check_in_date then
        raise exception 'Дата выезда должна быть позже даты заезда!!';
    end if;
    return new;
end;
$$ language plpgsql;

create or replace trigger trigger_valid_booking_dates
before insert or update on BOOKINGS
for each row
execute function validate_booking_dates();

-- обновление истории статусов комнат
create or replace function update_room_status_history()
returns trigger as $$
begin
    if new.status = 'подтверждено' then
        update ROOM_STATUS_HISTORY set valid_to = new.check_in_date
        where room_id = new.room_id and valid_to is null;

        insert into ROOM_STATUS_HISTORY (history_id, room_id, status, valid_from, valid_to)
        values ((select COALESCE(MAX(history_id), 0) + 1 from ROOM_STATUS_HISTORY),
                 new.room_id, 'занят', new.check_in_date, new.check_out_date);
    end if;
    return new;
end;
$$ language plpgsql;

create or replace trigger trigger_update_room_status
after insert or update on BOOKINGS
for each row
execute function update_room_status_history();


-- проверка уникальности email клиента
create or replace function check_email_unique()
returns trigger as $$
begin
    if exists (select 1
               from clients
               where email = new.email and client_id != new.client_id) then
        raise exception 'Ошибка. Данный email уже был зарегестрирован в системе';
    end if;
    return new;
end;
$$ language plpgsql;

create or replace constraint trigger trigger_check_email
after insert or update on clients
for each row
execute function check_email_unique();



