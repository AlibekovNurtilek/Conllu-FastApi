from conllu import parse
from tqdm import tqdm

def find_invalid_lines(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    invalid_lines = []
    valid_lines = []
    
    # Используем tqdm для прогресс-бара
    for i, line in enumerate(tqdm(lines, desc="Проверка строк", unit="строк"), start=1):  
        stripped = line.rstrip()  # Убираем пробелы справа
        
        if not stripped or stripped.startswith("#"):  
            valid_lines.append(stripped)
            continue  

        try:
            parse("\n".join(valid_lines + [stripped]))  
            valid_lines.append(stripped)  
        except Exception as e:
            invalid_lines.append((i, stripped, str(e)))

    print("\nАнализ завершён!")
    
    if invalid_lines:
        print("⚠ Найдены некорректные строки в CoNLL-U файле:")
        for line_num, content, error in invalid_lines:  # Выводим только первые 10 ошибок
            print(f"Строка {line_num}: {content} → Ошибка: {error}")
    else:
        print("✅ Файл полностью валиден, ошибок нет.")

# Запуск проверки
find_invalid_lines("data/mydata.conllu")
