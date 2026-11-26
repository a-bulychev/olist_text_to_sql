import streamlit as st
import pandas as pd
from src.pipeline import ask_database

# Настройка страницы
st.set_page_config(page_title="AI Text-to-SQL: Olist", page_icon="🤖", layout="wide")

st.title("🤖 AI Text-to-SQL на русском")
st.markdown("""
Этот проект использует локальную LLM (Qwen2.5-Coder) для перевода вопросов на русском языке 
в SQL-запросы к базе данных бразильского e-commerce **Olist**.
""")

# Боковая панель с примерами
with st.sidebar:
    st.header("Примеры вопросов:")
    examples = [
        "Сколько всего заказов было доставлено в 2017 году?",
        "Топ-5 городов по количеству клиентов.",
        "Сколько заказов было оплачено способом 'credit_card' в штате SP?",
        "Какая средняя стоимость доставки (freight_value) для товаров из категории 'brinquedos'?"
    ]
    for ex in examples:
        if st.button(ex):
            st.session_state['question'] = ex

# Поле ввода вопроса
question = st.text_input("Введите ваш вопрос к базе данных:", 
                         value=st.session_state.get('question', 'Сколько всего заказов было оформлено в 2018 году?'))

if st.button("Сгенерировать SQL и выполнить", type="primary"):
    if question:
        with st.spinner("Генерирую SQL и запрашиваю данные..."):
            result = ask_database(question)
            
            if result["status"] == "success":
                # Показываем сгенерированный SQL в раскрывающемся блоке
                with st.expander("Посмотреть сгенерированный SQL-запрос", expanded=True):
                    st.code(result["sql"], language="sql")
                
                # Показываем результат
                st.subheader("Результат запроса:")
                if len(result["data"]) > 0:
                    st.dataframe(result["data"], use_container_width=True)
                    st.caption(f"Найдено строк: {len(result['data'])}")
                else:
                    st.info("Запрос выполнен успешно, но не вернул данных.")
            else:
                st.error(f"Произошла ошибка: {result['error']}")
                if result['sql']:
                    st.code(result['sql'], language="sql")
    else:
        st.warning("Пожалуйста, введите вопрос.")