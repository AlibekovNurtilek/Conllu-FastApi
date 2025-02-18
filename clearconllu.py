import re

def isHead(token: str) -> bool:
    """ Проверяет, является ли токен допустимым значением HEAD в CoNLL-U. """
    return token.isdigit() and int(token) >= 0

def isDeprel(token: str) -> bool:
    """ Проверяет, является ли токен допустимым значением DEPREL в CoNLL-U. """
    VALID_DEPREL = {
        "root", "nsubj", "obj", "iobj", "csubj", "ccomp", "xcomp", "advcl", "obl",
        "vocative", "discourse", "conj", "cc", "case", "det", "amod", "nmod",
        "appos", "nummod", "acl", "compound", "punct", 'cop', 'aux', 'parataxis', "punct", "det"
    }
    return token in VALID_DEPREL
def fix_conllu_line(line):
    # Разделяем строку на колонки по табуляции
    #columns = re.split(r'\s+', line.strip())  # Разделение по пробелам и табуляциям
    columns = line.strip().split("\t")
    try:

        
        if len(columns) < 10:
            columns += ["_"] * (10 - len(columns))

        # Если строка имеет больше 10 колонок, удаляем лишние
        if len(columns) > 10:
            # Перед удалением лишних колонок проверяем, если значение не равно "_", выводим sent_id
            for i in range(10, len(columns)):
                if columns[i] != "_":
                    print(f"sent_id: {columns[0]} - Проверить колонку {i + 1}: {columns[i]}")
            columns = columns[:10]  # Оставляем только первые 10 колонок
        
        
        # Проверяем HEAD и DEPREL
        if not isHead(columns[6]):
            if isHead(columns[7]):
                columns[6], columns[7] = columns[7], columns[6]

        # Проверяем DEPREL
        if not isDeprel(columns[7]):
            if isDeprel(columns[8]):
                # Меняем местами DEPREL и DEPS
                columns[7], columns[8] = columns[8], columns[7]
        for i in range(3, len(columns)):
                    if columns[i] == '-':
                        columns[i] = "_"

        # Если все поля HEAD, DEPREL, DEPS и MISC равны "_", оставляем их без изменений
        if len(columns) >= 10 and columns[6] == "_" and columns[7] == "_" and columns[8] == "_" and columns[9] == "_":
            return line.strip()  # Возвращаем строку без изменений

        # Возвращаем исправленную строку
        return "\t".join(columns)

    except IndexError as e:
        print(f"Ошибка: Выход за пределы индекса на строке: {line.strip()}")
        return line.strip()  # Возвращаем строку без изменений в случае ошибки

def correct_conllu_file(input_file_path, output_file_path):
    with open(input_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    corrected_lines = []
    
    for line in lines:
        # Пропускаем комментарии и пустые строки
        if line.startswith("#") or not line.strip():
            corrected_lines.append(line.strip())
        else:
            corrected_line = fix_conllu_line(line)
            corrected_lines.append(corrected_line)
    
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(corrected_lines))

# Пример использования
input_file = "data/mydata_corrected_3.conllu"  # Путь к исходному файлу
output_file = "data/mydata_corrected_3.conllu"  # Путь к исправленному файлу

correct_conllu_file(input_file, output_file)

print("Файл успешно исправлен!")
