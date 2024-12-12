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

    async def add_vehicle(self, user_id, vehicle_id):
        if self.conn is None:
            await self.connect()

        query1 = "UPDATE users SET vehicle_id = ? WHERE user_id = ?"
        await self.execute_query(query1, (vehicle_id, user_id))

        # Второй запрос для вставки в таблицу num_car
        query2 = "INSERT INTO num_car (vehicle_id) VALUES (?)"
        await self.execute_query(query2, (vehicle_id,))

    # ==============Добовляем пользователя===============================
    async def add_user(self, user_id: int, username: str, name: str, last_name: str, iphone: int,
                       date_reg: int):  # Добавление пользователя, name, last_name, iphone, date_reg):  # Добавление пользователя
        if self.conn is None:
            await self.connect()

        if await db.user_exists(user_id, username):  # Проверка на существование пользователя
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

    async def user_exists(self, user_id: int, username: str) -> bool:
        query = "SELECT COUNT(*) FROM users WHERE user_id = ? AND username = ?"
        result = await self.execute_query(query, (user_id, username))
        return result[0][0] > 0

    async def car_exists(self, car_number: str) -> bool:
        query = "SELECT COUNT(*) FROM num_car WHERE vehicle_id = ?"
        result = await self.execute_query(query, (car_number,))
        return result[0][0] > 0

    async def info_number_car(self, user_id: int):  # Получение количества автомобилей
        query = "SELECT vehicle_id IS NOT NULL FROM users WHERE user_id = ?"
        result = await self.execute_query(query, (user_id,))
        return result[0][0] > 0

    async def create_tables(self) -> None:  # Создание таблицы
        if self.conn is None:
            await self.connect()

        # Создание таблиц для SQLite

        await self.execute_query('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE NULL,
            username TEXT NULL,
            name TEXT NULL,
            last_name TEXT NULL,
            iphone VARCHAR(20) NULL,
            date_reg INTEGER NULL,
            vehicle_id TEXT NULL,
            vehicle_cpec BIT NULL
        )
        ''')

        await self.execute_query('''
            CREATE TABLE IF NOT EXISTS num_car (
            id INTEGER PRIMARY KEY,
            vehicle_id TEXT NULL,
            vehicle_name TEXT NULL
        )
        ''')

    async def create_car_table(self, car_number: str = None) -> None:
        if self.conn is None:
            await self.connect()

        table_name = f"car_{car_number.replace(' ', '_')}"  # Заменяем пробелы на подчеркивания
        query = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY,
                    date INTEGER NOT NULL,
                    start_km VARCHAR(999999999) NOT NULL,
                    end_km VARCHAR(999999999) NOT NULL,
                    total_km VARCHAR(999999999) NOT NULL,
                    fuel_start VARCHAR(999999999) NOT NULL,
                    fuel_end VARCHAR(999999999) NOT NULL,
                    fuel_refuel VARCHAR(999999999) NULL,
                    user_name TEXT NULL,
                    special_equipment VARCHAR(999) NULL,
                    nuber_car INTEGER NOT NULL
                    )
                """
        await self.execute_query(query)


db = DataBase('sqlite.db')  # подключение БД
