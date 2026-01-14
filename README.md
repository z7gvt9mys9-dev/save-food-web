# Save Food Web

**Платформа для борьбы с пищевыми отходами**  
Приложение помогает находить, отдавать и забирать еду, которая иначе была бы выброшена. Соединяет кафе, рестораны, магазины, волонтёров и людей, желающих забрать еду бесплатно или по символической цене.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18-blue)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)

## Основные возможности

- Карта с ближайшими точками раздачи еды (Яндекс.Карты)
- Профили пользователей и организаций (регистрация, авторизация)
- Публикация объявлений о доступной еде (с фото, описанием, сроком годности)
- Уведомления о новых предложениях в радиусе
- Система отзывов и рейтинга
- Админ-панель для модерации

## Технологии

**Frontend**  
- React 18  
- Vite (сборка)  
- react-yandex-maps  
- Lucide-react (иконки)  
- Tailwind CSS / CSS-модули  

**Backend**  
- Python 3.12+  
- FastAPI  
- SQLAlchemy + SQLite (можно перейти на PostgreSQL)  
- Pydantic  
- Uvicorn  

**Дополнительно**  
- Яндекс.Карты API (геокодирование + маршруты)  
- JWT авторизация  

## Структура проекта
save-food-web/
├── backend/              # FastAPI бэкенд
│   ├── app/              # основная логика
│   ├── database.py
│   ├── main.py
│   └── requirements.txt
├── project/              # React фронтенд
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   ├── context/
│   │   └── App.jsx
│   ├── public/
│   └── vite.config.js
├── savefood.db           # локальная база (не коммитить!)
├── .gitignore
└── README.md



## Установка и запуск

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

API будет доступен на: http://localhost:8000
Swagger-документация: http://localhost:8000/docs

## 2. Frontend
cd project
npm install
npm run dev

Открывается на: http://localhost:5173 (или другой порт Vite)
3. База данных
Проект использует SQLite (savefood.db).
Для первого запуска создайте таблицы через FastAPI или вручную:

# В backend можно добавить init-скрипт
# или просто зарегистрировать первого пользователя через /register

Текущий статус проекта

Карта с проектами/точками работает (Яндекс.Карты)
Геолокация + fallback на Красную площадь
Маршруты (через свой API или прямой линией)
Базовая авторизация и профили (в разработке)

Планы на развитие

Полная авторизация + Google OAuth
Фото загрузка объявлений
Push-уведомления
Фильтры по типу еды, расстоянию, времени
Мобильная адаптивность
Переход на PostgreSQL + Docker
Деплой (Vercel + Render / Railway)



Контакты / вопросы
GitHub: @z7gvt9mys9-dev
Email: (igel2020i@gmail.com)
Telegram: (@toksyaFoksya)