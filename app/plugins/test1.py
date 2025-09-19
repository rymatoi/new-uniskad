import os


def collect_python_files(directory, output_file):
    # Открываем файл для записи
    with open(output_file, 'w', encoding='utf-8') as f:
        # Рекурсивно обходим все папки и файлы
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    # Получаем относительный путь к файлу
                    relative_path = os.path.relpath(os.path.join(root, file), directory)

                    # Записываем разделитель и путь к файлу
                    f.write('\n' + '=' * 80 + '\n')
                    f.write(f'Файл: {relative_path}\n')
                    f.write('=' * 80 + '\n\n')

                    # Читаем и записываем содержимое файла
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as py_file:
                            content = py_file.read()
                            f.write(content)
                            f.write('\n')
                    except Exception as e:
                        f.write(f'Ошибка при чтении файла: {str(e)}\n')


# Пример использования
if __name__ == '__main__':
    output_file = 'python_files_content.txt'

    collect_python_files(r'C:\Users\kisatsuki\PycharmProjects\new-uniskad 3.0\app\plugins\project', output_file)
    print(f'Готово! Результат сохранен в файл: {output_file}')
