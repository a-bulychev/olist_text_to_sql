import duckdb
from pathlib import Path

# Пути к папкам и файлу базы данных
DATA_DIR = Path("data")
DB_PATH = "olist.duckdb"

# Словарь: название таблицы в БД -> имя CSV-файла в папке data
FILES = {
    "orders":               "olist_orders_dataset.csv",
    "order_items":          "olist_order_items_dataset.csv",
    "order_payments":       "olist_order_payments_dataset.csv",
    "order_reviews":        "olist_order_reviews_dataset.csv",
    "customers":            "olist_customers_dataset.csv",
    "sellers":              "olist_sellers_dataset.csv",
    "products":             "olist_products_dataset.csv",
    "geolocation":          "olist_geolocation_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

def main():
    # Подключаемся к DuckDB (файл создастся автоматически)
    con = duckdb.connect(DB_PATH)
    
    print("Начинаю загрузку данных из CSV в DuckDB...\n")
    
    for table_name, filename in FILES.items():
        file_path = DATA_DIR / filename
        
        # Проверяем, существует ли файл
        if not file_path.exists():
            print(f"[ПРОПУСК] Файл {file_path} не найден. Убедитесь, что он лежит в папке data/")
            continue
            
        # Удаляем таблицу, если она уже была создана ранее (чтобы избежать ошибок при повторном запуске)
        con.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Создаем таблицу напрямую из CSV. read_csv_auto сам определит типы данных и заголовки.
        con.execute(f"""
            CREATE TABLE {table_name} AS 
            SELECT * FROM read_csv_auto('{file_path}', header=True)
        """)
        
        # Считаем количество загруженных строк для проверки
        row_count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"[OK] Таблица '{table_name}': загружено {row_count:,} строк")
        
    con.close()
    print(f"\nГотово! База данных сохранена в файл: {DB_PATH}")

if __name__ == "__main__":
    main()