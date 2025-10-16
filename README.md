# Использование

Клонируйте репозиторий:

```git clone https://github.com/petr5092/QA-bot```


Установите зависимости:

```pip install -r requirements.txt```


Возможно, понадобится вручную скачать некоторые библиотеки NLTK.
Откройте Python-консоль и выполните:
```
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

Или просто запустите установку:
```
python setup.py
```

Активируйте виртуальную среду и запустите сервер так:
```
uvicorn main:app --host 127.0.0.2 --port 9013 --reload
```
Видео работы проекта:

https://disk.yandex.ru/i/2DfR16vnrPaQHA
