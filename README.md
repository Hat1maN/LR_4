# Django XML/JSON App

## Описание
Приложение на Django для работы с данными о марках:  
- Ввод через HTML-форму с последующим сохранением в XML  
- Загрузка XML-файлов на сервер с валидацией  
- Просмотр содержимого всех XML-файлов на сайте  

Все настройки формы, сообщений и пути к файлам централизованы в `brands_app/config.py`.  
Добавление новых полей и изменение текста осуществляется только через этот файл.

## Установка и запуск

1. Клонировать репозиторий или скачать файлы:
```bash
git clone <https://github.com/Hat1maN/LR_4>
cd <LR4>
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/macOS
pip install django lxml
python manage.py runserver
Перейти в браузере:
http://127.0.0.1:8000/ — форма добавления марки
http://127.0.0.1:8000/upload/ — загрузка XML
http://127.0.0.1:8000/list/ — просмотр всех XML