"""
Программа для поиска дубликатов email-адресов в файле анкет.
"""

import argparse
import re
from typing import List, Dict, Optional


def is_valid_email(email: str) -> bool:
    """
    Проверяет, является ли строка корректным email.
    Допустимые домены: gmail.com, mail.ru, yandex.ru
    Локальная часть: буквы, цифры, . _ % + - , длина до 64 символов.
    """
    pattern = r'^[A-Za-z0-9._%+-]{1,64}@(gmail\.com|mail\.ru|yandex\.ru)$'
    return bool(re.fullmatch(pattern, email.strip()))


def parse_contact(contact: str) -> Optional[str]:
    """
    Возвращает email, если это email, иначе None.
    Если это не email — пропускаем анкету.
    """
    contact_clean = contact.strip()  # Очистка от пробелов
    if is_valid_email(contact_clean):
        return contact_clean
    else:
        return None  # Не email — игнорируем анкету


def read_file(file_path: str) -> str:
    """
    Читает содержимое файла и возвращает как строку.
    :param file_path: путь к файлу
    :return: содержимое файла
    :raises FileNotFoundError: если файл не найден
    :raises UnicodeDecodeError: если файл не в UTF-8
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл '{file_path}' не найден.")
    except UnicodeDecodeError:
        raise UnicodeDecodeError("Файл должен быть в кодировке UTF-8.")


def parse_persons(raw_text: str) -> List[Dict]:
    """
    Парсит текст файла и возвращает список словарей с данными анкет.

    Формат анкеты:
    45)
    Фамилия: Гусева
    Имя: Анна
    Пол: Женский
    Дата рождения: 25.05.1992
    Номер телефона или email: anna123456@mail.ru
    Город: Саранск
    """
    persons = []
    blocks = raw_text.strip().split('\n\n')

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 6:  # Пропускаем короткие блоки
            continue

        # Убираем номер анкеты (например, "45)")
        if lines[0].endswith(')'):
            lines = lines[1:]  # Удаляем первую строку с номером

        # Извлекаем данные по ключам
        surname = extract_value(lines[0], "Фамилия:")
        name = extract_value(lines[1], "Имя:")
        gender = extract_value(lines[2], "Пол:")
        birth_date = extract_value(lines[3], "Дата рождения:")
        contact = extract_value(lines[4], "Номер телефона или email:")
        city = extract_value(lines[5], "Город:")

        if not all([surname, name, gender, birth_date, contact, city]):
            continue  # Пропускаем некорректные анкеты

        # Проверяем, является ли контакт email
        email = parse_contact(contact)
        if email is None:
            continue  # Пропускаем анкеты с номерами телефонов

        person = {
            "surname": surname,
            "name": name,
            "gender": gender,
            "birth_date": birth_date,
            "email": email,
            "city": city,
            "raw_data": block
        }
        persons.append(person)

    return persons


def extract_value(line: str, prefix: str) -> str:
    """
    Извлекает значение после префикса.
    Пример: "Фамилия: Гусева" → "Гусева"
    """
    if line.startswith(prefix):
        return line[len(prefix):].strip()
    return ""


def find_duplicate_emails(persons: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Находит дубликаты email-адресов.

    :param persons: список анкет
    :return: словарь email -> список анкет с этим email
    """
    email_to_persons = {}

    for person in persons:
        email = person["email"]
        if email not in email_to_persons:
            email_to_persons[email] = []
        email_to_persons[email].append(person)

    # Оставляем только те email, которые встречаются более одного раза
    duplicates = {email: people for email, people in email_to_persons.items() if len(people) > 1}
    return duplicates

def print_duplicates(duplicates: Dict[str, List[Dict]]) -> None:
    """
    Выводит анкеты с дубликатами email на экран.
    """
    if not duplicates:
        print("Дубликатов email не найдено.")
        return

    print("=" * 50)
    print("Найдены дубликаты email:")
    print("=" * 50)

    for email, persons_list in duplicates.items():
        print(f"\nEmail: {email}")
        print("-" * 30)
        for person in persons_list:
            print(person["raw_data"])
            print("-" * 30)

def main() -> None:
    """
    Основная функция программы.
    """
    parser = argparse.ArgumentParser(description="Поиск дубликатов email в файле анкет.")
    parser.add_argument('filename', type=str, help='Имя файла с анкетами (например, data.txt)')
    args = parser.parse_args()

    try:
        # Читаем содержимое файла
        content = read_file(args.filename)

        # Парсим анкеты
        persons = parse_persons(content)

        # Ищем дубликаты email
        duplicates = find_duplicate_emails(persons)

        # Выводим дубликаты
        print_duplicates(duplicates)

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    main()