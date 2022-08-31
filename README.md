# CI и CD проекта foodgram

![workflow](https://github.com/Alex9568rus/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание проекта

host: 84.252.139.89
админка:
имя пользователя: alex
пароль: alex

Cайт Foodgram, «Продуктовый помощник» - онлайн-сервис и API для него. На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

---

## Технологии

* Django
* Django Rest Framework
* Nginx
* Postgresql
* Docker
* Docker compose
* Яндекс.Облако

---

## Запуск проекта

Для запуска проекта вам понадобится:
* зарегистрироваться на DockerHub;
* создать сервер (например, на Яндекс.Облаке).

Настройка удаленного сервера будет описана далее.

1. ___Клонировать репозиторий:___

` git clone git@github.com:Alex9568rus/foodgram-project-react.git`

2. ___Добавить секретные данные:___

Для добавления секретной информации нужно зайти в склонированный репозиторий -> раздел settings -> Secrets -> Actions
и добавить поочередно следующие переменные:
| Название переменной | Значение |
|:----:|:----:|
|SECRET_KEY| SECRET_KEY из settings.py|
|YOUR_TELEGRAM_ID|ID чата, в который будут приходить уведомления|
|TELEGRAM_BOT_TOKEN|Токен телеграм-бота|
|USERNAME|Ваш логин на DockerHub|
|PASSWORD|Ваш пароль от DockerHub|
|HOST|Публичный IP сервера на Яндекс.Облаке|
|USER|Ваш логин на Яндекс.Облаке|
|SSH_KEY|Приватный ключ с локальной машины|
|PASSPHRASE|Пароль, указанный при создании ключей|
|DB_ENGINE|В проекте использовался postgresql|
|DB_NAME|Имя вашей базы данных|
|POSTGRES_USER|Ваш логин для подключения к базе данных|
|POSTGRES_PASSWORD|Пароль для подключения к БД|
|DB_HOST|Название сервиса (контейнера)|
|DB_PORT|Порт для подключения к БД |

3. ___Настройка сервера:___

* На боевом сервере установите docker и docker-compose
* Остановите службу nginx
* Скопируйте файлы docker-compose.yaml и nginx.conf из проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx.conf соответственно

4. ___Deploy:___

При git pus запускается скрипт GitHub actions который выполняет автоматический deploy на сервер.

После успешного деплоя необходимо на сервере выполнить следующие дествия:
* ` sudo docker-compose exec web python3 manage.py migrate` - сделать миграции;
* ` sudo docker-compose exec web python3 manage.py createsuperuser` - создать суперюзера;
* ` sudo docker-compose exec web python3 manage.py collectstatic --no-input` - сабрать статику
* ` sudo docker-compose exec web python3 import_ings_and_tags_csv.py` - для добавления игредиентов в БД

Чтобы создать резервную копию базы данных воспользуйтесь командой:

` sudo docker-compose exec web python manage.py dumpdata > fixtures.json`

---

## Автор
___Жбаков А.___

_https://github.com/Alex9568rus_

