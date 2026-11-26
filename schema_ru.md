# Схема данных Olist

**Диалект SQL: DuckDB** (совместим с SQLite на 95%, поддерживает `strftime`, `date_trunc`, `extract`).

**Важные соглашения о значениях:**
- Поля `*_city` — в **нижнем регистре без диакритики**: `sao paulo`, `rio de janeiro`.
- Поля `*_state` — в **ВЕРХНЕМ регистре**: `SP`, `RJ`.
- `order_status` принимает: `delivered`, `shipped`, `canceled`, `unavailable`, `invoiced`, `processing`, `created`, `approved`.
- `payment_type` принимает: `credit_card`, `boleto`, `voucher`, `debit_card`.
- Все даты — строки формата `YYYY-MM-DD HH:MM:SS`; для года используйте `strftime('%Y', col)`.

## 1. orders — заказы
| Поле | Описание |
|---|---|
| order_id | Уникальный идентификатор заказа |
| customer_id | ID клиента (FK → customers.customer_id) |
| order_status | Статус заказа |
| order_purchase_timestamp | Дата и время оформления заказа |
| order_delivered_customer_date | Дата фактической доставки клиенту |

## 2. order_items — позиции заказов
| Поле | Описание |
|---|---|
| order_id | ID заказа |
| product_id | ID товара |
| seller_id | ID продавца |
| price | Цена товара в BRL |
| freight_value | Стоимость доставки в BRL |

## 3. customers — клиенты
| Поле | Описание |
|---|---|
| customer_id | ID клиента в контексте заказа (PK) |
| customer_unique_id | Постоянный ID человека (может повторяться) |
| customer_city | Город в нижнем регистре |
| customer_state | Штат, 2 буквы (верхний регистр) |

## 4. products — товары
| Поле | Описание |
|---|---|
| product_id | ID товара (PK) |
| product_category_name | Категория на португальском |

## 5. order_payments — платежи
| Поле | Описание |
|---|---|
| order_id | ID заказа |
| payment_type | Способ оплаты |
| payment_value | Сумма платежа в BRL |

## 6. order_reviews — отзывы
| Поле | Описание |
|---|---|
| review_id | ID отзыва |
| order_id | ID заказа |
| review_score | Оценка 1–5 |