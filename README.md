# Парсер сайта https://rosreestr.gov.ru/wps/portal/p/cc_present/ir_egrn

Это доработанный репозиторий https://github.com/Tatikoma/rosreestr-ownership-parser

## Запуск API

1. Настроить конфиг-файлы
2. Установить php, postgreSQL, python > 3.5
3. Установить пакеты pip: peewee, flask, flask_cors, backoff
4. Создать таблицу rr в PostgreSQL
```
 CREATE TABLE public.rr (                                       +
     id integer DEFAULT nextval('rr_id_seq'::regclass) NOT NULL,+
     cadastral_no text  NULL,                                   +
     region text  NULL,                                         +
     status integer  NULL,                                      +
     r_key integer  NULL,                                       +
     date_added integer  NULL,                                  +
     date_updated integer  NULL,                                +
     rosreestr_id text  NULL,                                   +
     url text  NULL,                                            +
     guid text  NULL,                                           +
     next integer  NULL
 );
```
5. Запустить swagger api (Можно в tmux)
```
python3 app.py
```
6. Проверить по адресу localhost:5070/
7. Настройка NGINX
```
    location /rosreestr/ {
        proxy_pass          http://localhost:5070;
        proxy_set_header    Host        $host;
        proxy_set_header    X-Real-IP   $remote_addr;
    }
``` 
8. Запустить в tmux для каждого ключа свой скрипт, например, если три ключа, то параллельно запускается:
```
python3 start.py --id=0
python3 start.py --id=1
python3 start.py --id=2
```
9. Запустить скачивание zip-архивов (в tmux)
```
php ir_egrn_download.php
```

## Конфиг-файлы

1. config.php - заменить на нужное кол-во ключей, заменить на PostgreSQL данные, вставить ключ anticaptcha
```
$rosreestr_keys = [
    'ключ1',
    'ключ2',
    'ключ3',
];
$config = [
    'rosreestr_key' => $rosreestr_keys[0], // API ключ Росреестра по умолчанию на всякий
    'rosreestr_interval' => 900, // не используется
    'rosreestr_hang_timer' => 198010, // через 55 часов переставать ждать ответа на выписку
    'captcha_method' => 'anticaptcha', // captcha_solver (бесплатно) или anticaptcha (платно)
    'anticaptcha_key' => 'anticaptcha_key', // API ключ anti-captcha.com
    'db' => [
        'pgsql:host=localhost;dbname=dbname;',
        'dbuser',
        'dbpass'
    ]
];
```
2. config.py - заменить на PostgreSQL данные и заменить на нужное кол-во ключей
``` 
DB_USER="DB_USER"
DB_NAME="DB_NAME"
DB_PASS="DB_PASS"
DB_HOST="DB_HOST"

r_ids = [
    'ключ1',
    'ключ2',
    'ключ3',
]
```
