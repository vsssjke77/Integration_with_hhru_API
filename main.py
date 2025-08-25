import time
from dataclasses import dataclass, asdict
from typing import Optional

import requests
import json

url = 'https://api.hh.ru/vacancies'

@dataclass
class VacancyData:
    salary: Optional[dict]  # зарплата может быть None или словарём с минимумом и максимумом
    name: str              # название вакансии
    link: str              # ссылка на вакансию
    area: str

def extract_vacancy_data(item: dict) -> VacancyData:
    return VacancyData(
        salary=item.get('salary'),
        name=item.get('name'),
        link=item.get('alternate_url', ''),  # ссылка на вакансию
        area=item.get('area', '')
    )

def retry_request(retry: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(retry):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    print("Запрос не увенчался успехом")
                    time.sleep(2)
            raise Exception("Все попытки запроса исчерпаны")
        return wrapper
    return decorator

@retry_request(3)
def fetch_vacancies(url: str, page: int = 0):
    query_params = {
        "text": "python backend",
        "per_page": 100,
        "page": page,
        "experience": "noExperience"
    }
    response = requests.get(url, query_params)
    if response.status_code != 200:
        raise ValueError

    print(f"Успешно получены вакансии на странице {page}")
    result = response.json()
    return result

def fetch_all_vacancies(url: str):
    page = 0
    vacancies_data = []
    while True:
        if page == 20:
            break
        vacancies = fetch_vacancies(url,page)

        if len(vacancies["items"]) == 0:
            break

        vacancies_data.extend([extract_vacancy_data(item) for item in vacancies["items"]])
        page += 1
        time.sleep(0.2)
    with open("vacancies2.json", "w", encoding='utf-8') as file:
        json.dump([asdict(v) for v in vacancies_data], file, ensure_ascii=False, indent=4)

def main():
    fetch_all_vacancies(url)


if __name__ == "__main__":
    main()