import duckdb

# Подключение к базе
con = duckdb.connect("olist.duckdb", read_only=True)

# Список эталонных запросов
queries = {
    "Доставлено в 2017": "SELECT COUNT(*) FROM orders WHERE order_status = 'delivered' AND strftime('%Y', order_purchase_timestamp) = '2017'",
    "Клиенты из Сан-Паулу": "SELECT COUNT(DISTINCT customer_unique_id) FROM customers JOIN orders ON customers.customer_id = orders.customer_id WHERE customer_city = 'sao paulo'",
        "Оплата картой в SP": "SELECT COUNT(DISTINCT o.order_id) FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN order_payments p ON o.order_id = p.order_id WHERE p.payment_type = 'credit_card' AND c.customer_state = 'SP'",
    "Средняя доставка игрушек": "SELECT AVG(oi.freight_value) FROM order_items oi JOIN products p ON oi.product_id = p.product_id WHERE p.product_category_name = 'brinquedos'",
    "Отзывы на 5 звезд": "SELECT COUNT(*) FROM order_reviews WHERE review_score = 5"
}

print("Эталонные ответы (Ground Truth):\n")
for name, sql in queries.items():
    result = con.execute(sql).fetchone()[0]
    # Если результат дробный (как средняя стоимость), округляем до 2 знаков
    if isinstance(result, float):
        result = round(result, 2)
    print(f"{name}: {result}")

con.close()