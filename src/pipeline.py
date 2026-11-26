import json
import re
import duckdb
import requests
from pathlib import Path

# --- Настройки ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b-instruct-q5_K_M"
DB_PATH = "olist.duckdb"
FEW_SHOT_PATH = Path("examples/few_shot_ru.json")

# --- 1. Загрузка few-shot примеров ---
def load_few_shots():
    with open(FEW_SHOT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# --- 2. Формирование промпта ---
def build_prompt(user_question, few_shots):
    # Базовое описание схемы (для экономии токенов берем только нужные таблицы, 
    # но для универсальности пока передадим основное)
    schema_info = """
    Схема БД (DuckDB):
    - orders(order_id, customer_id, order_status, order_purchase_timestamp)
    - customers(customer_id, customer_unique_id, customer_city, customer_state)
    - order_items(order_id, product_id, price, freight_value)
    - products(product_id, product_category_name)
    - order_payments(order_id, payment_type, payment_value)
    - order_reviews(review_id, order_id, review_score)
    
    ВАЖНО: 
    1. Города в нижнем регистре (например, 'sao paulo'). Штаты в ВЕРХНЕМ регистре (например, 'SP', 'RJ').
    2. Для дат используй strftime('%Y', column) или date_trunc.
    3. Если считаешь клиентов, используй COUNT(DISTINCT customer_unique_id).
    4. Таблица с отзывами называется строго 'order_reviews'.
    """
    
    examples_text = "\n".join([
        f"Вопрос: {ex['question']}\nSQL: {ex['sql']}" 
        for ex in few_shots
    ])

    prompt = f"""Ты — эксперт по SQL (диалект DuckDB).
Используй только SELECT запросы.

{schema_info}

Примеры правильных запросов:
{examples_text}

Вопрос пользователя: {user_question}
Верни ТОЛЬКО SQL-запрос, без объяснений и без markdown-разметки.
SQL:"""
    return prompt

# --- 3. Запрос к Ollama ---
def generate_sql(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,  # минимум креативности для SQL
            "num_ctx": 4096
        }
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json().get("response", "")

# --- 4. Очистка от markdown ---
def clean_sql(raw_text):
    # Убираем блоки ```sql ... ```
    text = re.sub(r"```(?:sql)?\s*", "", raw_text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()
    # Убеждаемся, что запрос заканчивается на точку с запятой
    if not text.endswith(";"):
        text += ";"
    return text

# --- 5. Валидация безопасности ---
def validate_sql(sql):
    sql_upper = sql.upper()
    forbidden_words = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    for word in forbidden_words:
        if word in sql_upper:
            raise ValueError(f"⚠️ ОПАСНО: Запрос содержит запрещенную команду {word}")
    if not (sql_upper.startswith("SELECT") or sql_upper.startswith("WITH")):
        raise ValueError("⚠️ ОПАСНО: Разрешены только SELECT или WITH запросы.")
    return True

# --- Обновленная главная функция ---
def ask_database(question):
    try:
        # 1. Готовим промпт
        few_shots = load_few_shots()
        prompt = build_prompt(question, few_shots)
        
        # 2. Спрашиваем модель
        raw_response = generate_sql(prompt)
        
        # 3. Чистим и валидируем
        sql_query = clean_sql(raw_response)
        validate_sql(sql_query)
        
        # 4. Выполняем в DuckDB
        con = duckdb.connect(DB_PATH, read_only=True)
        result = con.execute(sql_query).df()
        con.close()
        
        return {"status": "success", "sql": sql_query, "data": result, "error": None}
    except Exception as e:
        return {"status": "error", "sql": locals().get('sql_query', ''), "data": None, "error": str(e)}

if __name__ == "__main__":
    # Оставим для теста в терминале
    res = ask_database("Сколько уникальных клиентов из города Сан-Паулу сделали хотя бы один заказ?")
    print(res['sql'])
    print(res['data'])