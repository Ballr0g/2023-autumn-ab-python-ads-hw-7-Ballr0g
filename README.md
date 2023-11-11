[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/CVuseC5w)

# 2023-autumn-ab-python-ads-HW-6
## Общее описание
Дополнить HW5 работой с базой данных, тестированием методов API и настроить автоматический запуск линтеров и тестов при push в репозиторий.

## API endpoints
| endpoint | Обновить существующий endpoint | Создать новый endpoint | Тип запроса | Действие | Подсказка |
| --- | :---: | :---: | --- | --- | --- |
| /predict/{baseline} | :heavy_check_mark: | | POST | Возвращает предсказание класса (fraud/clean) для заданного входного текста **и записывает входной текст, предсказание, используемый бейзлайн и время выполнения в базу ``messages.db``** | |
| /get_latest_entry/{baseline} | | :heavy_check_mark: | GET | Возвращает крайнюю запись в БД ``messages.db`` для бейзлайна ``baseline``| Используйте код вида ``db.query(model).filter(column == value)`` |
| /get_number_of_entries | | ✔️ | GET | Возвращает количество записей в БД ``messages.db`` для каждого бейзлайна, например: ``{"constant-fraud": 1, "constant-clean": 2, "first-hypothesis": 3}`` | Используйте код вида ``db.query(column1, column2).group_by(column2)`` и функцию ``sqlalchemy.func.count`` |

## Тестирование API
Реализовать тесты для каждого метода API. Для /get_number_of_entries и /get_latest_entry достаточно реализовать только проверку ``response_code`` при правильном и неправильном запросе, для остальных - также добавить проверку ``response_body``.

## Actions
Настроить автоматический запуск ``make lint`` и ``make test`` при каждом push в репозиторий.


## Критерии оценки
| Критерий | Количество баллов |
| - | - | 
| Реализованы модули ``database.py`` и ``models.py`` для работы с БД | **+1** |
| Реализованы и корректно работают все необходимые методы API | **+4** |
| Реализованы все тесты | **+3**|
| Реализован и корректно отрабатывает workflow ``lint_and_test_on_push.yaml ``| **+2**|