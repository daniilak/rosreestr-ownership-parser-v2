<?php
// https://rosreestr.gov.ru/wps/portal/p/cc_present/ir_egrn
include_once('lib/init.php');
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