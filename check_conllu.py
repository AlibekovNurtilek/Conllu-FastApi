from conllu import parse
from tqdm import tqdm

def find_invalid_lines(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    invalid_blocks = []
    block = []
    block_start_line = 0
    current_line_number = 0

    for line in tqdm(lines, desc="Проверка предложений", unit="строк"):
        current_line_number += 1
        stripped = line.rstrip()

        if not stripped:
            if block:
                # Проверим блок
                try:
                    parse("\n".join(block))
                except Exception as e:
                    invalid_blocks.append((block_start_line, block, str(e)))
                block = []
            continue

        if not block:
            block_start_line = current_line_number
        block.append(stripped)

    # Проверка последнего блока, если файл не заканчивается пустой строкой
    if block:
        try:
            parse("\n".join(block))
        except Exception as e:
            invalid_blocks.append((block_start_line, block, str(e)))

    print("\nАнализ завершён!")

    if invalid_blocks:
        print(f"⚠ Найдено {len(invalid_blocks)} некорректных предложений:")
        for line_num, block, error in invalid_blocks[:10]:  # показываем только первые 10
            print(f"\nСтрока {line_num}: Ошибка: {error}")
            for l in block:
                print(f"  {l}")
    else:
        print("✅ Файл полностью валиден, ошибок нет.")

# Запуск проверки
find_invalid_lines("data/mydata.conllu")
