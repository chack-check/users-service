# Chack Check Users Service

Сервис, управляющий пользователями и аутентификацией

## Предустановка

Надо поставить docker compose, ну и make, для удобства

## Запуск проекта

Для дев окружения `.env` файлик лежит в репе, не игнорится. Поэтому пока не буду описывать env vars

Непосредственно запуск:

### make

```
$ make dev
```

### docker compose plugin

```
$ docker compose -f docker-compose.dev.yml up --build
```