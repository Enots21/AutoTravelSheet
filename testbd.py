import asyncio
import unittest

from DB.database import db


class RunnerTest(unittest.TestCase):
    def test_db_add_user(self):
        asyncio.run(db.add_car_info(1, '12.12.24', '115780', '115820', '40', '52.23', '42.63', '0',
                                    'Александров Даниил', '0', 'A321AA21'))
