from pipeline import ask_database

TEST_CASES = [
    {
        "question": "Сколько всего заказов было доставлено в 2017 году?",
        "expected_answer": 43428  # <-- Вставьте вашу цифру
    },
    {
        "question": "Сколько уникальных клиентов из города Сан-Паулу сделали хотя бы один заказ?",
        "expected_answer": 14984  # <-- Вставьте вашу цифру
    },
    {
        "question": "Сколько заказов было оплачено способом 'credit_card' в штате SP?",
        "expected_answer": 32074  # <-- Вставьте вашу цифру
    },
    {
        "question": "Какая средняя стоимость доставки (freight_value) для товаров из категории 'brinquedos'?",
        "expected_answer": 18.81   # <-- Вставьте вашу цифру
    },
    {
        "question": "Сколько всего отзывов с оценкой 5?",
        "expected_answer": 57328  # <-- Вставьте вашу цифру
    }
]

def run_evaluation():
    correct = 0
    total = len(TEST_CASES)
    
    print("Запуск оценки (Execution Accuracy)...\n")
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"Тест {i}: {test['question']}")
        result = ask_database(test["question"])
        
        if result["status"] == "success" and not result["data"].empty:
            # Берем первое значение из первой колонки
            generated_answer = result["data"].iloc[0, 0]
            
            # Проверка: если число дробное, сравниваем с округлением до 2 знаков
            if isinstance(generated_answer, float) or isinstance(test['expected_answer'], float):
                is_correct = round(float(generated_answer), 2) == round(float(test['expected_answer']), 2)
            else:
                is_correct = int(generated_answer) == int(test['expected_answer'])
            
            if is_correct:
                print(f" ✅ Верно! (Ожидалось {test['expected_answer']}, получено {generated_answer})\n")
                correct += 1
            else:
                print(f" ❌ Ошибка. Ожидалось {test['expected_answer']}, получено {generated_answer}\n")
        else:
            print(f" ❌ Ошибка выполнения запроса: {result.get('error')}\n")

    accuracy = (correct / total) * 100
    print(f"Итоговая точность (Execution Accuracy): {accuracy:.1f}% ({correct}/{total})")

if __name__ == "__main__":
    run_evaluation()