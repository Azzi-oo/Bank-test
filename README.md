# Bank API tests

## Allure-отчёт

Плагин `allure-pytest` устанавливается из `requirements.txt`. Allure CLI
на macOS устанавливается отдельно: `brew install allure`.

```sh
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
allure serve allure-results
```

Для запуска без банковского API используйте `python -m pytest tests/unit -v`.
Настройки `pytest.ini` включают сбор результатов и очистку предыдущего прогона.
Чтобы сохранить HTML-отчёт:

```sh
allure generate allure-results --clean -o allure-report
allure open allure-report
```

В разделе Behaviors API-сценарии сгруппированы по `Bank API → функциональность →
положительные/негативные сценарии`. У тестов русские названия и важность.
Внутри теста видны действия пользователя, вложенные HTTP-вызовы, проверки статуса
и результата операции. Подготовка и удаление пользователей видны в фикстурах.
В HTTP-шаге приложены JSON запроса и ответа. Поля с password, token,
authorization, cookie и secret в названии маскируются рекурсивно;
заголовки и не-JSON тела не прикладываются. Это фильтрация этих вложений,
а не всех возможных логов и traceback: не публикуйте отчёты с реальными секретами.

Для нового теста добавьте название и историю, а проверки оформите контекстным шагом:

```python
import allure

@allure.title("Новый счёт имеет нулевой баланс")
@allure.story("Положительные сценарии")
def test_new_account(make_user):
    user = make_user(UserRole.USER)
    account = user.create_account()
    with allure.step("Проверить начальный баланс"):
        assert account.balance == 0
```

Общие методы Steps уже содержат шаги; повторять их в тесте не нужно.
Для методов с паролем используется `with allure.step(...)`, чтобы аргументы
метода не записывались автоматически как параметры декорированного шага.

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

## Проверки PostgreSQL

Зависимости SQLAlchemy и psycopg2-binary включены в `requirements.txt`.
URL читается из `BANK_DATABASE_URL`, а если переменная не задана — из
`dataBaseUrl` в `resources/urls.properties`. Формат драйвера:
`postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE`.
`backendUrl` из properties не используется: адрес API по-прежнему задаётся
через `BANK_API_URL` в `config.py`.

```sh
# Все тесты, включая проверки сохранения данных
python -m pytest -v --db

# Только сценарии API + PostgreSQL
python -m pytest -v --db -m db
allure serve allure-results
```

Без `--db` девять БД-сценариев явно пропускаются; остальные API- и unit-тесты
работают без подключения к PostgreSQL. При `--db` ошибка подключения считается
ошибкой теста, а не пропуском.

`db_engine` создаёт пул лениво и освобождает его в конце сессии pytest.
`db_session` выдаёт отдельную SQLAlchemy Session на тест, открывает транзакцию
только для чтения и закрывает её даже при падении. Уровень READ COMMITTED
позволяет видеть изменения, закоммиченные API между запросами.
Повторный поиск обновляет уже загруженный ORM-объект (`populate_existing=True`).

Модель `User` соответствует таблице `user` банковского приложения:
`id`, `username`, `role`, `deleted_at`. Поле пароля не загружается.
Тесты проверяют сохранение пользователя, отметку логического удаления
и отсутствие записи после отклонения некорректного пароля.
Создание и очистка выполняются через существующие API-фикстуры;
SQL-записей и изменения схемы приложения нет. Allure показывает шаги чтения
и вложения с выбранными полями записи.

`test_accounts_db.py`, `test_transfers_db.py` и `test_credits_db.py` проверяют:
- deposit: баланс счёта и единственную транзакцию пополнения;
- transfer: списание и зачисление на оба счёта, сумму и направление перевода;
- credit: сумму, срок, задолженность кредита и зачисление на счёт;
- repay: списание, нулевую задолженность и транзакцию со ссылкой на кредит;
- отсутствие изменений в БД при запрещённом кредите и частичном погашении.

Модели `Account`, `Credit`, `Transaction` соответствуют таблицам `account`,
`credit`, `transaction`. Фикстура `bank_db` предоставляет чтение через `BankCrudDb`.
Фикстура `bank_db_steps` предоставляет `BankDbSteps`: проверки данных и Allure-шаги
вынесены в `src/main/api/steps/bank_db_steps.py`. В тестах остаются подготовка,
API-операция и вызов метода проверки; Allure-декораторы описывают сценарий.
Суммы и сроки для API- и DB-сценариев создаёт `BankDataGenerator` из
`src/main/api/generators/bank_data_generator.py` через фикстуру `bank_data`.
Генератор использует стандартный `random`; диапазоны заданы в одном месте.
Перевод меньше пополнения, частичное погашение меньше кредита, срок — 1–60 месяцев.
Для точного сравнения с DOUBLE PRECISION суммы пополнений и переводов имеют
шаг 0.25. Ожидаемые балансы вычисляются из входных данных, которые приложены в Allure.
Проверки используют свежие данные после API-операций и выводят записи в Allure.
В текущем приложении `credit_issuance` создаётся через обычное пополнение
без `transaction.credit_id`; связь выдаваемого кредита проверяется через
`credit.account_id`. Для `credit_repayment` проверяется и `transaction.credit_id`.

Если получаете `role "symfony" does not exist`, проверьте, что обращаетесь к БД
контейнера, а не к другой PostgreSQL на том же порту:

```sh
lsof -nP -iTCP:5432 -sTCP:LISTEN
docker ps --format '{{.Names}}\t{{.Ports}}'
```

При конфликте нужен отдельный порт Docker PostgreSQL и соответствующий
`BANK_DATABASE_URL`, либо согласованная остановка локального PostgreSQL.

В текущем локальном окружении `resources/urls.properties` использует адрес
компьютера `192.168.0.10:5432`, через который доступна БД контейнера `bank_api`.
Это позволяет оставить локальный PostgreSQL на `localhost:5432` работающим.
При смене сетевого адреса компьютера обновите `dataBaseUrl` или задайте
`BANK_DATABASE_URL` для БД приложения.
