# Платформа для блогов

Данный проект создан в рамках обучения Яндекс Практикум:
```
Авторы:  Сарвилин Алексей
```

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/sarvilin/hw05_final
```

```
cd hw05_final
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