[![Version](https://img.shields.io/badge/version-v0.1.0-informational)](https://github.com/SPBUnited/serviz/actions/workflows/auto-semver.yml)
[![CI smoke (build + up)](https://github.com/SPbUnited/PAcmaCS/actions/workflows/ci-smoke.yaml/badge.svg?branch=fb4)](https://github.com/SPbUnited/PAcmaCS/actions/workflows/ci-smoke.yaml)

# PACS - Programmatically Actionable Cybernetic Studio

Данный монорепозиторий содержит набор модулей новой структуры системы управления команды SPbUnited:

- SerViz (VIZualization SERver) - веб-интерфейс визуализации
- TransNet (NETwork TRANSformer)

## Реализованные функции

### PACS

- Связь между модулями через zmq (ipc)
- Автоматическая установка зависимостей, сборка и запуск сервисов

### SERVIZ

- Отрисовка игрового поля с объектами на поле в реальном времени. Реализованные объекты:
  - Роботы
  - Мяч
  - Произвольные линии
  - Многоугольники
  - Круги (точки)
- Поддержка множества слоев с настройкой видимости для каждого слоя и настройкой высоты

## Документация

- [Справка по формату межпроцессных сообщений](docs/zmq_api_v3.md)
- [Serviz draw API](docs/serviz_draw_api.md)
- [Serviz telemetry API](docs/serviz_telemetry_api.md)

## Зависимости

- Python 3.12+
- Node.js 18
- jq

## Установка и запуск

Установите зависимости и соберите проект:

```bash
make install
make init
```

Запустите все сервисы:

```bash
make up
```

После запуска можно подключится к serviz по адресу http://localhost:8000

## Обновление до новой версии

Подтяните изменения из удаленного репозитория:

```
git pull
```

Заного соберите проект:

```
make init
```

## Более подробное описание реализованных инструкций:

- `make install` - устанавливает необходимые системные пакеты
- `make init` - инициализирует виртуальное окружение и зависимости
- `make up` - запускает все внутренние (только необходимые) сервисы
