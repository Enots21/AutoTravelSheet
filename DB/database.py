import logging
import aiosqlite


class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    async def connect(self):  # connect to database
        self.conn = await aiosqlite.connect(self.db_name)

    async def disconnect(self):  # disconnect from database
        if self.conn:
            await self.conn.close()

    async def execute_query(self, query, *args):  # Запрос базы данных
        if self.conn is None:
            await self.connect()
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, *args)
            result = await cursor.fetchall()
        await self.conn.commit()

        return result

    async def fetch_vehicle_info(self, vehicle_numbers: str):
        if self.conn is None:
            await self.connect()

        try:
            query = """
                        SELECT 
                            vehicle_name, 
                            special_equipment, 
                            vehicle_numbers
                        FROM num_car 
                        WHERE vehicle_numbers = ?
                    """
            result = await self.execute_query(query, (vehicle_numbers,))
            return result  # Возвращает список кортежей или пустой список, если ничего не найдено
        except Exception as e:
            logging.error(e)

    async def add_vehicle(self, vehicle_numbers: str, vehicle_name: str, special_equipment: int, user_id: int):
        if self.conn is None:
            await self.connect()

        try:
            # Проверяем, есть ли уже такой номер автомобиля
            query_check = """SELECT id FROM num_car WHERE vehicle_numbers = ?"""
            existing_vehicle = await self.execute_query(query_check, (vehicle_numbers,))

            if existing_vehicle:  # Номер уже существует
                vehicle_id = existing_vehicle[0][0] if existing_vehicle else None
                query3 = """INSERT INTO user_numbers (user_id, number_id) VALUES (?, ?)"""
                await self.execute_query(query3, (user_id, vehicle_id))
                print(f"Номер {vehicle_numbers} присвоен пользователю {user_id}")

            else:
                query1 = """INSERT OR IGNORE INTO num_car (vehicle_numbers, vehicle_name, special_equipment) 
                VALUES (?, ?, ?)"""
                logging.info(f'Номер {vehicle_numbers} добавлен в базу данных {user_id}')
                await self.execute_query(query1, (vehicle_numbers, vehicle_name, special_equipment))

                query2 = """SELECT last_insert_rowid()"""
                last_inserted_id = await self.execute_query(query2)
                vehicle_id = last_inserted_id[0][0] if last_inserted_id else None

                if vehicle_id:
                    query3 = """INSERT INTO user_numbers (user_id, number_id) VALUES (?, ?)"""
                    await self.execute_query(query3, (user_id, vehicle_id))
                    print(f"Номер {vehicle_numbers} добавлен и присвоен пользователю {user_id}")
                else:
                    print("Не удалось получить последний вставленный идентификатор.")
        except Exception as e:
            logging.error(f'Ошибка при добавлении пользователя {user_id} в базу данных {vehicle_numbers}')
            print(f"Произошла ошибка: {e}")

    # ==============Добовляем пользователя===============================
    async def add_user(self, user_id: int, username, name: str, last_name: str, iphone: int,
                       date_reg: int):  # Добавление пользователя, name, last_name, iphone, date_reg):
        # Добавление пользователя
        if self.conn is None:
            await self.connect()

        if await db.user_exists(user_id):  # Проверка на существование пользователя
            pass

        # Добавляем пользователя
        await self.execute_query("""
            INSERT OR REPLACE INTO users
            (user_id, username, name, last_name, iphone, date_reg) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, name, last_name, iphone, date_reg))
        # ==========================================================

    async def get_user(self, user_id):
        query = 'SELECT name, last_name FROM users WHERE user_id = ?'
        result = await self.execute_query(query, (user_id,))
        if result:  # Проверяем, есть ли пользователь
            name, last_name = result[0]  # Доступ к первому элементу кортежа (кортеж внутри списка) и распаковка
            return {'name': name, 'last_name': last_name}
        else:
            return None  # или другое значение, обозначающее отсутствие пользователя

    # ==========================================================

    async def user_exists(self, user_id: int) -> bool:
        query = "SELECT COUNT(*) FROM users WHERE user_id = ?"
        result = await self.execute_query(query, (user_id,))
        return result[0][0] > 0

    async def car_exists(self, vehicle_numbers: str, user_id: int) -> bool:
        query_check = """SELECT id FROM num_car WHERE vehicle_numbers = ?"""
        existing_vehicle = await self.execute_query(query_check, (vehicle_numbers,))

        if existing_vehicle:  # Номер уже существует
            vehicle_id = existing_vehicle[0][0] if existing_vehicle else None
            query3 = """INSERT INTO user_numbers (user_id, number_id) VALUES (?, ?)"""
            await self.execute_query(query3, (user_id, vehicle_id))
            logging.info(f"Номер {vehicle_numbers} присвоен пользователю {user_id}")
            return True
        else:
            return False

    async def get_veh_id(self, vehicle_numbers: int):
        query = 'SELECT Special_Equipment FROM num_car WHERE vehicle_numbers = ?'
        result = await self.execute_query(query, (vehicle_numbers,))
        return result[0]  #

    async def fetch_vehicle_info_by_user_id(self, user_id):
        if self.conn is None:
            await self.connect()

        query = ('''
            SELECT
                n.vehicle_numbers,
                n.vehicle_name
            FROM
                user_numbers AS un
            JOIN
                num_car AS n ON un.number_id = n.id
            WHERE
                un.user_id = ?
        ''')
        result = await self.execute_query(query, (user_id,))
        return result

    async def add_car_info(self, truck_number, drivers_name, date, departure_time, arrival_time, starting_odometer,
                           ending_odometer, total_mileage, special_equipment, fuel_consumed, starting_fuel,
                           ending_fuel):
        if self.conn is None:
            await self.connect()

        query = f"""
                    INSERT INTO car_{truck_number}
                    (Truck_Number, Drivers_Name, Date, Departure_Time, Arrival_Time, Starting_Odometer,
                    Ending_Odometer, Total_Mileage, Special_Equipment, Fuel_Consumed, Starting_Fuel,
                    Ending_Fuel)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
        await self.execute_query(query, (truck_number, drivers_name, date, departure_time, arrival_time,
                                         starting_odometer, ending_odometer, total_mileage,
                                         special_equipment, fuel_consumed, starting_fuel, ending_fuel))

    async def info_number_car(self, user_id: int):  # Проверка на наличие автомобиля в базе
        query = '''SELECT EXISTS(SELECT 1 FROM user_numbers WHERE user_id = ?) as num_car'''
        result = await self.execute_query(query, (user_id,))

        # Возвращаем True или False в зависимости от результата
        return bool(result[0][0]) if result else False

    async def list_car_numbers(self, user_id: int):
        if self.conn is None:
            await self.connect()

        query = '''SELECT COUNT(*) FROM user_numbers WHERE user_id = ?'''
        result = await self.execute_query(query, (user_id,))
        return result[0][0]

    async def create_tables(self) -> None:  # Создание таблицы
        if self.conn is None:
            await self.connect()

        # Создание таблиц для SQLite

        # ID - id строки в таблице
        # user_id - id пользователя
        # username - имя пользователя
        # name - имя
        # last_name - фамилия
        # iphone - телефон
        # date_reg - дата регистрации
        # vehicle_list - список автомобилей

        await self.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE NULL NOT NULL,
            username TEXT NULL,
            name TEXT NULL,
            last_name TEXT NULL,
            iphone VARCHAR(20) NULL,
            date_reg INTEGER NULL
        )
        ''')

        await self.execute_query('''
            CREATE TABLE IF NOT EXISTS user_numbers (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NULL,
            number_id INTEGER NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (number_id) REFERENCES num_car(number_id)
            )
        ''')

        await self.execute_query('''
            CREATE TABLE IF NOT EXISTS num_car (
            id INTEGER PRIMARY KEY,
            number_id INTEGER UNIQUE,
            vehicle_numbers TEXT NULL,
            vehicle_name TEXT NULL,
            special_equipment VARCHAR(999) NULL
            )
        ''')

        # vehicle_numbers - номера автомобилей
        # vehicle_name - имена автомобилей
        #

    async def create_car_table(self, car_number: str = None) -> None:
        if self.conn is None:
            await self.connect()

        table_name = f"car_{car_number.replace(' ', '_')}"  # Заменяем пробелы на подчеркивания
        query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    Truck_Number INTEGER NOT NULL,
                    Drivers_Name TEXT NOT NULL,
                    Date INTEGER NOT NULL,
                    Departure_Time INTEGER NOT NULL,
                    Arrival_Time INTEGER NOT NULL,
                    Starting_Odometer VARCHAR(999999999) NULL,
                    Ending_Odometer VARCHAR(999999999) NULL,      
                    Total_Mileage VARCHAR(999999999) NULL,
                    Special_Equipment VARCHAR(999) NULL,
                    Fuel_Consumed VARCHAR(999999999) NULL,
                    Starting_Fuel VARCHAR(999999999) NULL,
                    Ending_Fuel VARCHAR(999999999) NULL
                    )
                """
        await self.execute_query(query)
        # | Гос. номер:        | А123ВВ178             |
        # | ФИО водителя:      | Иванов Иван Иванович  |
        # | Дата:              | 27.10.2024            |
        # | Время выезда:      | 08:00                 |
        # | Время прибытия:    | 10:00                 |
        # | Пробег (начальный): | 15000                |
        # | Пробег (конечный): | 15050                 |
        # | Общий пробег:      | 50                    |
        # | Спец.Оборудование: | 3 л.час         |
        # | Расход топлива (литров): | 100             |
        # | Начальное расход топлива (литров): | 100   |
        # | Конечный расход топлива (литров): | 100    |


db = DataBase('sqlite.db')  # подключение БД
