import os
from dotenv import load_dotenv
import psycopg
from psycopg import sql

# Инициализируем настройки из вашего .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Читаем параметры из окружения (синхронизировано с settings.py)
target_db = os.getenv('DATABASE_NAME', 'skyprodb')
db_user = os.getenv('DATABASE_USER')
db_password = os.getenv('DATABASE_PASSWORD')
db_host = os.getenv('DATABASE_HOST', 'localhost')
db_port = os.getenv('DATABASE_PORT', '5432')

print(f"Подключение к PostgreSQL для создания базы '{target_db}'...")

try:
    # Подключаемся к служебной базе 'postgres', используя ваши учетные данные
    with psycopg.connect(
            dbname='postgres',
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            autocommit=True  # Обязательно для CREATE DATABASE
    ) as conn:

        with conn.cursor() as cur:
            # Проверяем, существует ли уже целевая база данных
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_db,))
            exists = cur.fetchone()

            if not exists:
                # Безопасно подставляем имя базы через экранирование параметров
                cur.execute(
                    sql.SQL("CREATE DATABASE {};").format(sql.Identifier(target_db))
                )
                print(f" Success: База данных '{target_db}' успешно создана!")
            else:
                print(f" Info: База данных '{target_db}' уже существует.")

except Exception as e:
    print(f" Error: Не удалось создать базу данных. Ошибка: {e}")
