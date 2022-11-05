# Платформа для блогов

## Описание
Предусмотрена регистрация и авторизация пользователей, создание
и редактирование записей, загрузка картинок к постам, подписка
на пользователя или группу, лента, комментарии к записям.

К проекту написаны тесты (Unittest)

## Технологии
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/sarvilin/yatube
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Сгенерировать и указать SECRET_KEY:
```
создать файл:  hw05_final/yatube/yatube/.env
добавить строку: SECRET_KEY = '<ВАШ СЕКРЕТНЫЙ КЛЮЧ>'
```

Выполнить миграции:
```
python3 yatube/manage.py migrate
```

Запустить проект:
```
python3 yatube/manage.py runserver
```

URL проекта:  http://127.0.0.1:8000/

### *Backend by:*
[Сарвилин Алексей](https://github.com/sarvilin/yatube)

Данный проект создан в рамках обучения Яндекс Практикум