# Production Deployment Guide

## Обзор

Этот документ описывает процесс развертывания приложения Proton Bot в продакшн с использованием GitHub Actions workflow.

## Workflow: Production Release

### Триггеры

Workflow запускается только вручную через GitHub Actions UI (`workflow_dispatch`).

### Параметры запуска

| Параметр | Описание | Обязательный | По умолчанию | Опции |
|----------|----------|--------------|--------------|-------|
| `environment` | Целевое окружение | Да | `production` | `production`, `staging` |
| `version` | Версия релиза | Нет | Автоматическая | Любая строка |
| `skip_tests` | Пропустить тесты | Нет | `false` | `true`, `false` |
| `force_deploy` | Принудительный деплой | Нет | `false` | `true`, `false` |

### Этапы выполнения

#### 1. Validate (Валидация)
- Проверка наличия необходимых secrets
- Проверка ветки (рекомендуется main)
- Валидация конфигурации

#### 2. Test (Тестирование)
- Запуск полного набора тестов
- Генерация отчета о покрытии кода
- Пропускается если `skip_tests=true`

#### 3. Build (Сборка)
- Сборка Docker образа
- Генерация тега версии
- Кэширование для ускорения сборки

#### 4. Deploy (Развертывание)
- Создание бэкапа текущей версии
- Обновление кода на сервере
- Запуск скрипта развертывания
- Проверка статуса сервиса

#### 5. Rollback (Откат)
- Автоматический откат при неудачном деплое
- Восстановление из последнего бэкапа

## Как запустить деплой

### Через GitHub UI

1. Перейдите в раздел **Actions** репозитория
2. Выберите workflow **Production Release**
3. Нажмите **Run workflow**
4. Заполните параметры:
   - **Environment**: `production` или `staging`
   - **Version**: версия релиза (опционально)
   - **Skip tests**: только в экстренных случаях
   - **Force deploy**: только при необходимости
5. Нажмите **Run workflow**

### Через GitHub CLI

```bash
# Базовый деплой в продакшн
gh workflow run "Production Release" \
  --field environment=production

# Деплой с указанием версии
gh workflow run "Production Release" \
  --field environment=production \
  --field version=v1.2.3

# Деплой в staging
gh workflow run "Production Release" \
  --field environment=staging \
  --field version=staging-$(date +%Y%m%d)
```

## Требования

### Secrets в GitHub

Убедитесь, что в настройках репозитория добавлены следующие secrets:

- `SSH_PRIVATE_KEY` - приватный SSH ключ для доступа к серверу
- `BOT_TOKEN` - токен Telegram бота
- `API_URL` - URL API (если используется)
- `NOTIFY_SECRET` - секрет для уведомлений

### Сервер

- SSH доступ к серверу `158.160.46.65`
- Пользователь `vorobevavd`
- Установленные Docker или Podman
- Директория приложения: `~/telegram-bot-final` (production) или `~/telegram-bot-staging` (staging)

## Мониторинг деплоя

### Логи

Все логи доступны в разделе **Actions** GitHub:
- Детальные логи каждого шага
- Время выполнения
- Статус выполнения

### Проверка статуса

После деплоя проверьте:

```bash
# Подключение к серверу
ssh vorobevavd@158.160.46.65

# Проверка контейнера
docker ps | grep tg-bot

# Просмотр логов
docker logs tg-bot

# Проверка статуса приложения
curl -f http://localhost:8000/health || echo "Service not responding"
```

## Откат (Rollback)

### Автоматический откат

Workflow автоматически выполняет откат при неудачном деплое в продакшн.

### Ручной откат

```bash
# Подключение к серверу
ssh vorobevavd@158.160.46.65

# Поиск бэкапов
ls -la ~/telegram-bot-final.backup.*

# Откат к конкретному бэкапу
BACKUP_DIR="~/telegram-bot-final.backup.20241201-143022"
cd ~/telegram-bot-final
docker stop tg-bot
docker rm tg-bot
rm -rf ~/telegram-bot-final
cp -r $BACKUP_DIR ~/telegram-bot-final
cd ~/telegram-bot-final
./deploy.sh
```

## Безопасность

### Рекомендации

1. **Никогда не используйте `skip_tests=true`** в продакшн без крайней необходимости
2. **Всегда проверяйте логи** после деплоя
3. **Используйте staging** для тестирования изменений
4. **Делайте бэкапы** перед критическими изменениями

### Ограничения

- Деплой возможен только из ветки `main` (или с `force_deploy=true`)
- Требуется подтверждение для продакшн окружения
- Автоматический откат только для продакшн

## Устранение неполадок

### Частые проблемы

#### 1. Ошибка SSH подключения
```
Error: Permission denied (publickey)
```
**Решение**: Проверьте `SSH_PRIVATE_KEY` secret

#### 2. Ошибка сборки Docker
```
Error: failed to build image
```
**Решение**: Проверьте `Dockerfile` и зависимости

#### 3. Сервис не запускается
```
Error: Container is not running
```
**Решение**: Проверьте логи контейнера и переменные окружения

#### 4. Тесты не проходят
```
Error: Tests failed
```
**Решение**: Исправьте код или используйте `force_deploy=true` (не рекомендуется)

### Контакты

При возникновении проблем обращайтесь к команде разработки или создавайте issue в репозитории.

## Changelog

- **v1.0.0** - Первоначальная версия workflow
- Добавлена поддержка staging окружения
- Добавлен автоматический откат
- Добавлена валидация окружения
- Добавлены уведомления о статусе
