# База данных системы управления отелями

### Введение

##### ***Цель работы:***
Получение практических навыков работы с промышленными СУБД, проектирование БД (концептуальное, логическое, физическое), создание хранимых процедур, представлений, триггеров, индексов. Разработка системы управления бронированием отелей.

-------
#### ***Инструменты***:
PostgreSQL 16, GitLab CI/CD

--------
#### ***Описание проекта:***
Система управления бронированием отелей с функционалом:
- Учёт отелей, номеров и их характеристик
- Управление бронированиями
- Обработка платежей
- Управление отзывами клиентов
- История статусов номеров (SCD Type 2)

----------

#### ***Предметная область и сущности:***

**Основные сущности:**
1. **Отели** - информация об отелях (название, категория, местоположение)
2. **Номера** - информация о номерах в отелях (тип, цена, вместимость)
3. **Клиенты** - данные клиентов отеля
4. **Бронирования** - информация о бронированиях номеров
5. **Платежи** - данные о платежах за бронирования
6. **Отзывы** - отзывы клиентов об отелях
7. **Услуги отеля** - дополнительные услуги, предоставляемые отелем
8. **История статусов номеров** - временная история изменения статусов номеров (SCD Type 2)

-------

### ***Подробное описание сущностей***

1. **Отели (HOTELS)**
   - `hotel_id` - уникальный идентификатор
   - `name` - название отеля
   - `stars` - категория (1-5 звёзд)
   - `city` - город расположения
   - `email` - контактный email

2. **Номера (ROOMS)**
   - `room_id` - уникальный идентификатор
   - `hotel_id` - ссылка на отель
   - `room_type` - тип номера
   - `price` - стоимость за ночь
   - `capacity` - вместимость (кол-во гостей)

3. **Бронирования (BOOKINGS)**
   - `booking_id` - уникальный идентификатор
   - `client_id` - ссылка на клиента
   - `room_id` - ссылка на номер
   - `check_in_date` - дата заезда
   - `check_out_date` - дата выезда
   - `total_price` - общая стоимость
   - `status` - статус брони (подтверждено/отменено/завершено)

4. **История статусов номеров (ROOM_STATUS_HISTORY)**
   - `history_id` - уникальный идентификатор
   - `room_id` - ссылка на номер
   - `status` - статус (свободен/занят)
   - `valid_from` - дата начала действия статуса
   - `valid_to` - дата окончания действия статуса (NULL для текущего статуса)

-------

### ***Цель проекта:***
Разработка реляционной базы данных для системы управления бронированиями отелей, которая обеспечивает:

**Основные функции БД:**
- Хранение структурированных данных об отелях, номерах и клиентах
- Управление информацией о бронированиях с поддержкой различных статусов
- Фиксация платежных транзакций
- Хранение отзывов клиентов
- Ведение истории статусов номеров (SCD Type 2) для временного анализа

**Ожидаемые характеристики БД:**
- Нормализованная структура (3NF)
- Оптимизированные запросы для отчетности


### ***Актуальность***
Системы онлайн-бронирования являются критически важными для современной гостиничной индустрии, позволяя:
- Увеличить заполняемость отелей
- Оптимизировать процессы бронирования
- Улучшить использование клиентами систем бронирования
- Автоматизировать учёт и отчётность
