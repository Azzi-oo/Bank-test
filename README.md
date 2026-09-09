# Bank API tests

Python 3.12, pytest, requests и Pydantic 2. Тестируемое банковское приложение
запускается отдельно; по умолчанию API доступен на `http://localhost:4111`.

## Установка и запуск

```sh
python3.12 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

# Автономные проверки инфраструктуры, сервер не нужен
python -m pytest tests/unit -q

# Банковские сценарии на запущенном тестовом стенде
python -m pytest -m api -q

# Все тесты
python -m pytest -q
```

В `config.py` читаются переменные `BANK_API_URL`, `BANK_ADMIN_USERNAME`,
`BANK_ADMIN_PASSWORD`. Значения по умолчанию: `http://localhost:4111`,
`admin`, `123456`. `REQUEST_TIMEOUT` определяет сетевой таймаут.

## Структура

- `foundation/endpoint.py`: маршруты, HTTP-методы, успешные статусы и модели.
- `foundation/requesters/crud_requester.py`: HTTP-ответ без преобразования;
  принимает словари для негативных тестов и модели для обычных запросов.
- `foundation/requesters/validate_crud_requester.py`: валидация запроса,
  проверка статуса до чтения JSON, преобразование ответа в Pydantic-модель.
- `models/`: схемы запросов и ответов. JSON-алиасы переводят snake_case
  в camelCase, денежные значения ответов представлены через Decimal.
- `specs/`: заголовки и повторно используемые проверки HTTP-статусов.
- `steps/`: действия администратора и пользователя.
- `classes/api_manager.py`: HTTP-сессия и создание авторизованных шагов.
- `fixtures/`: инициализация менеджера, вход администратора, очистка пользователей.
- `tests/`: API-сценарии; `tests/unit` в корне — автономные проверки инфраструктуры.

`BaseClient` — общий транспорт. Тесты используют Steps; старые отдельные
клиенты и неиспользуемый протокол CrudEndpoint удалены.
Авторизация передаётся на каждом запросе, а не записывается в общие заголовки Session.

## Как писать тесты

Для положительного сценария используйте шаги: они проверяют успешный HTTP-статус
и структуру ответа. В тесте проверяется результат бизнес-операции:

```python
from decimal import Decimal
from src.main.api.models.requests import UserRole


def test_deposit(make_user):
    user = make_user(UserRole.USER)
    account = user.create_account()
    user.deposit(account.id, 1000.50)
    assert user.get_account(account.id).balance == Decimal("1000.50")
```

Для негативного сценария отправляйте словарь через `raw()`, чтобы Pydantic
не отклонил невалидные данные до запроса к серверу:

```python
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.specs.response_specs import ResponseSpecs

response = user.raw(Endpoint.CREDIT_REQUEST, ResponseSpecs.status(403)).post({
    "accountId": account.id,
    "amount": 5000,
    "termMonths": 12,
})
```

Новые API-тесты размещайте в `src/main/api/tests`, помечайте `pytest.mark.api`.
Для нового маршрута добавьте модели, конфигурацию Endpoint и метод Steps.
Не импортируйте фикстуры из тестов в прикладные классы.

## Жизненный цикл тестовых данных

Каждый тест получает собственную Session. `make_user` и `admin_steps` подключают
`created_obj`: созданные через AdminSteps пользователи регистрируются по ID и
удаляются после теста запросом `DELETE /api/admin/users/{user_id}`. Это выполняется
и при падении теста. Ошибка удаления одного пользователя не мешает попыткам удалить
остальных; ошибки отображаются как ошибки teardown. Session закрывается после очистки.
Массовое удаление не используется. Работайте с тестовым стендом.

Если негативный тест неожиданно создал пользователя через raw-запрос, его ID нужно
добавить в `created_obj` до проверки ожидаемого статуса. Метод
`admin_steps.create_invalid_user(...)` делает это автоматически и проверяет HTTP 400.
Прямое использование ApiManager вне pytest требует явного закрытия через `close()`
и самостоятельной очистки созданных данных.

## Генерация тестовых данных

`RandomModelGenerator.generate(CreateUserRequest, role=UserRole.CREDIT_SECRET)`
создаёт запрос по метаданным `Annotated[..., CreationRule(regex=...)]`.
Единая модель запроса находится в `models/requests.py`; импорт из `models/user.py`
также поддерживается. Правила генерации не заменяют валидацию модели и не запрещают
отправлять негативные данные через raw-запросы.

Генератор принимает переопределения по именам полей, сохраняет значения по умолчанию
и фабрики, проверяет итоговую модель через Pydantic. Неизвестные имена полей
вызывают ошибку. Для обязательных полей без правила поддерживаются `str`, `int`,
`float`, `bool` и перечисления; для остальных типов нужно передать значение явно.
Дополнительные ограничения модели проверяются после генерации: при несовместимых
правилах или значениях возвращается ошибка валидации.
Для регулярных выражений используется `rstr==3.2.2` из `requirements.txt`.

Фикстура `create_user_request` создаёт пользователя и возвращает его запрос,
а `make_user(role)` возвращает авторизованные шаги. Обе используют генератор
и удаляют созданных пользователей после теста.

`user_steps.create_account()` использует текущую авторизацию.
`api_manager.user_steps.create_account(create_user_request)` сначала получает токен
пользователя и создаёт его счёт, сохраняя токен исходного объекта шагов.
`Endpoint.CREATE_ACCOUNT` — альтернативное имя `Endpoint.ACCOUNT_CREATE` с тем же
маршрутом `/api/account/create` и ожидаемым статусом 201.
