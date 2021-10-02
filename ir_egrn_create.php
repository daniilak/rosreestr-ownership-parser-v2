<?php
include_once('config.php');
print "start";
if(isset($argv[1]) && $argv[1] == '--help'){
    print "Скрипт для создания заявок во ФГИС ЕГРН" . PHP_EOL;
    print PHP_EOL;
    print "Usage: php ir_egrn_create.php" . PHP_EOL;
    exit;
}
if (!isset($argv[1])) {
    print "Usage: php ir_egrn_create.php 0 или 1" . PHP_EOL;
    exit();
}
$id = intval($argv[1]);


function get($config, $id, $rosreestr_keys) {
    $dbh = getDBH($config);
    $statement = $dbh->query("SELECT * FROM rr WHERE (status = 0 or status = -1) AND guid = '" . $rosreestr_keys[$id]. "';");
    $DONE = $dbh->prepare("UPDATE rr SET status = 1, rosreestr_id = :rosreestr_id,date_updated = :date_updated WHERE id = :id");
    $updateStatus = $dbh->prepare("UPDATE rr SET status = :status WHERE id = :id");
    
    while($row = $statement->fetch(PDO::FETCH_ASSOC)){
        $config['rosreestr_key'] = $row['guid'];
        var_dump($row);

        $egrn = new IR_EGRN($config);
        $request = $egrn->createRequest($row['cadastral_no'], $row['region'], $row['r_key']);
        if ($request > 0) {
            $DONE->execute([
                ':rosreestr_id' => $request,
                ':date_updated' => time(),
                ':id' => $row['id'],
            ]);
            var_dump("Успешно. Спим 600 секунд");
            return;
        }
        if ($request == -101) {
            $updateStatus->execute([
                ':status' => -3,
                ':id' => $row['id']
            ]);
            var_dump("Ответ request == -101. Статус в режим =Аннулировано=. Переход на выполнение следующей задачи");
            continue;
        }
        if ($request == -102) {
            var_dump("Ответ request == -102. findRegexp не нашел заказ, надо подождать 10 минут. Статус не меняется. Выход из текущего скрипта");
            return;
        }
        if ($request == -105) {
            if (substr($row['cadastral_no'], 0, 2) == "77" && $row['region'] == "Москва") {
                var_dump('Ответ request == -105.  Event itemClick not found!. Москва стала Московской областью. Переход на выполнение следующей задачи');
                $setMoscowObl = $dbh->prepare("UPDATE rr SET region = 'Московская область', status = 0 WHERE id = :id;");
                $setMoscowObl->execute([':id' => $row['id']]);
                continue;
            }
            if (substr($row['cadastral_no'], 0, 2) == "50" && $row['region'] == "Московская область") {
                var_dump('Ответ request == -105.  Event itemClick not found!. Московская область стала Москвой. Переход на выполнение следующей задачи');
                $setMoscowObl = $dbh->prepare("UPDATE rr SET region = 'Москва', status = 0 WHERE id = :id;");
                $setMoscowObl->execute([':id' => $row['id']]);
                continue;
            }
            var_dump('Ответ request == -105.  Event itemClick not found!. Статус "Не найдено". Переход на выполнение следующей задачи');
            $updateStatus->execute([':status' => -2,':id' => $row['id']]);
            continue;
        }

        if ($request == -100) {
            if ($row['status'] == -1) {
                var_dump('Ответ request == -100.  status был "-1". Переход в статус полной остановки (-2).Переход на выполнение следующей задачи');
                $updateStatus->execute([':status' => -2,':id' => $row['id']]);
                continue;
            }
            if ($row['status'] == 0) {
                var_dump('Ответ request == -100.  status был "0". Переход в статус полуостановки(-1).Переход на выполнение следующей задачи');
                $updateStatus->execute([':status' => -1,':id' => $row['id']]);
                continue;
            }
        }


    }
}


get($config, $id, $rosreestr_keys);
