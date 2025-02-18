
def look__line(line, metadata):
    columns = line.strip().split("\t")

    if len(columns) < 10:
        columns += ["_"] * (10 - len(columns))

    if columns[6] == "punct":
        print(columns, metadata)

def look_file(input_file_path):
    with open(input_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()  
        metadata = ''
    for line in lines:
        if line.startswith("#"):
            metadata = line
            continue
        look__line(line=line, metadata=metadata)
    
    
# Пример использования
input_file = "data/mydata_corrected_3.conllu"  # Путь к исходному файлу
look_file(input_file)