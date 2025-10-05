# StarLabs 0G Automation

Этот инструмент автоматизирует взаимодействие с различными функциями в сети, включая операции с токенами и смарт-контрактами

ТУТОРИАЛ - https://star-labs.gitbook.io/star-labs/0g/eng

## Доступные функции:
# ФАУСЕТЫ
"faucet" - получение токенов из фаусета
"faucet_tokens" - получение различных токенов

# ДЕПЛОЙ
"storagescan_deploy" - деплой контракта на StorageScan

# NFT
"conft_mint" - минт NFT и домена

# СВАПЫ
"swaps" - свап токенов

## Требования
- Python 3.11.6 или выше

## Установка

1. Клонируйте репозиторий
```bash
git clone https://github.com/0xStarLabs/StarLabs-0G.git
cd StarLabs-0G
```

2. Установите зависимости
```bash
pip install -r requirements.txt
```

3. Настройте конфигурацию в файле `config.yaml`

4. Добавьте ваши данные в следующие файлы:
- `data/private_keys.txt` - один приватный ключ на строку
- `data/proxies.txt` - один прокси на строку (формат: `user:pass@ip:port`)
   Поддерживаются только HTTP прокси

5. Запустите бот
```bash
python main.py
```

## Настройка логов
В `config.yaml` вы можете настроить отправку логов в Telegram:
- `SEND_TELEGRAM_LOGS: false` - включение/выключение логов в Telegram
- `TELEGRAM_BOT_TOKEN: "ваш_токен"` - токен бота Telegram (получить можно у @BotFather)
- `TELEGRAM_USERS_IDS: [ваш_id]` - ID пользователей Telegram для отправки логов

## Поддержка
- Telegram: https://t.me/StarLabsTech
- Чат: https://t.me/StarLabsChat
