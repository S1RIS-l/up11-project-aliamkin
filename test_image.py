import os

def check_files():
    files_to_check = [
        "resources/picture.png",
        "resources/IMG_16_001.png",
        "resources/IMG_16_099.png"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"Файл {file_path} есть")
        else:
            print(f"Файла {file_path} нет")

if __name__ == "__main__":
    check_files()