# Пассажирам.РФ - Информационная система для записи на курсы водителей

## 📋 Требования к системе

- Python 3.10 или выше
- Windows / Linux / MacOS

## 🚀 Быстрый запуск (3 команды)

### 1. Открыть терминал в папке проекта
```bash
cd C:\Users\DEMEXAM\Desktop\exam-Erik_Sargsyan


### 2. Активировать виртуальное окружение
Windows:

```bash
venv\Scripts\activate
MacOS/Linux:

```bash
source venv/bin/activate
### 3. Установить зависимости (если не установлены)
```bash
pip install -r requirements.txt
4. Создать таблицы базы данных и еще открыть pg admin
```bash
python init_db.py
### 5. Запустить сервер
bash
python -m uvicorn main:app --reload
🌐 Доступ к приложению
После запуска откройте браузер и перейдите по адресу:

text
http://127.0.0.1:8000