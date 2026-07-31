# Stripe Payment Shop

## Установка и запуск

### Локальный запуск

#### Режим Debug

В режиме Debug приложение работает с базой данных SQLite.

```bash
# 1. Клонировать репозиторий
git clone 
cd stripe_shop

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env файл
cp .env.example .env
# Заполнить файл своими значениями
# При установленном параметре DEBUG=True приложение работает с базой данных SQLite
# При выключенном параметре - с PostgreSQL
# В данном случае необходимо запустить PostgreSQL
# Проще всего запустить через контейнер в Docker
# 4.1. Создать контейнер для БД PostgreSQL
docker run --name postgres-stripe -e POSTGRES_PASSWORD=password -e POSTGRES_DB=stripe_db -p 5432:5432 -d postgres:15

# 5. Выполнить миграции
python manage.py makemigrations
python manage.py migrate

# 6. Создать суперпользователя
python manage.py createsuperuser

# 7. Загрузить данные из файла
python manage.py loaddata initial_data

# 8. Запустить сервер
python manage.py runserver
```

### Запуск через Docker

```bash
docker-compose up --build
```

#### Режим Production

В режиме Production


### Доступные страницы

- Админка http://localhost:8000/admin/
- Страница конкретного предмета: http://localhost:8000/item/{item_number}
- Получение ID Сессии покупки конкретного предмета: http://localhost:8000/buy/{item_number}
- Страница конкретного заказа: http://localhost:8000/order/{order_number}

### Особенности работы с системой Strip

Работа с системой находится в тестовом режиме с тестовыми ключами. 
Для выполнения оплаты необходимо ввести следующие значения:
- Адрес электронной почты: любой, например, example@example.com
- Номер карты: 4242 4242 4242 4242
- ММ/ГГ: любой месяц/год в будущем, например, 12/34
- CVV/CVC: любые 3 цифры
- Остальные поля заполняются заполняются по своему усмотрению