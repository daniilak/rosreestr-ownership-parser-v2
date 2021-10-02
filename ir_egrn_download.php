<?php

// $config = include __DIR__ . DIRECTORY_SEPARATOR . 'config.php';
include_once('config.php');
if(isset($argv[1]) && $argv[1] == '--help'){
    print "Скрипт для загрузки результатов заданий из ФГИС ЕГРН" . PHP_EOL;
    print PHP_EOL;
    print "Usage: php ir_egrn_download.php" . PHP_EOL;
    exit;
}

// status = 0 - в очереди
// status = 1 - загружен очередь росреестра
// status = 2 - готово, можно скачивать файл 
// status = 3 - не скачалось, больше 55 часов, next == 0
// status = 4 - не скачалось, больше 55 часов, next == 1
while (1) {
    $dbh = getDBH($config);
    // find request older than two days
    $statement = $dbh->query('SELECT * FROM rr where status = 1 or status = 3');
    $done = $dbh->prepare("UPDATE rr SET status = 2, url = :url WHERE id = :id");
    $status3 = $dbh->prepare("UPDATE rr SET status = 3, next = :next WHERE id = :id");
    $status4 = $dbh->prepare("UPDATE rr SET status = 4 WHERE id = :id");
    $status4ForFather = $dbh->prepare("UPDATE rr SET status = 4 WHERE next = :next");
    $inserting = $dbh->prepare(
        'INSERT INTO rr 
            (cadastral_no, region, status, r_key, date_added, next, guid)
            VALUES (:cadastral_no, :region, :status, :r_key, :date_added, :next, :guid)
        '
    );
    

    $counters = [
        'success' => 0,
        'deleted3' => 0,
        'deleted4' => 0,
        'delayed' => 0,
        'failure' => 0,
    ];
    while($row = $statement->fetch(PDO::FETCH_ASSOC)){
        $config['rosreestr_key'] = $row['guid'];
        $egrn = new IR_EGRN($config);

        try {
            print "Проверяем результат по заявке № " . $row['rosreestr_id'] .'id='. $row['id'] . PHP_EOL;
            $zipFile = $egrn->getResult($row['rosreestr_id']);
            if($zipFile){
                $done->execute([':url' => $row['rosreestr_id'].'.zip',':id' => $row['id'],]);
                $counters['success']++;
            }
            else{
                if ($row['status'] = 1) {
                    if($row['date_added'] + $config['rosreestr_hang_timer'] < time()) {
                        print "Обновляем статус №" . $row['rosreestr_id'] . PHP_EOL;
                        if ($row['next'] == 0) {
                            $time = time();
                            $inserting->execute([
                                ':cadastral_no' => $row['cadastral_no'],
                                ':region' => $row['region'],
                                ':status' => 0,
                                ':r_key' => $row['r_key'],
                                ':date_added' => $time,
                                ':next' => -1,
                                ':guid' => $row['guid'],
                            ]);
                            $getID = $dbh->prepare("SELECT id FROM rr WHERE status = 0 AND date_added = :date_added AND next = -1");
                            $getID->execute([':date_added' => $time]);
                            $nextID = $getID->fetch(PDO::FETCH_ASSOC);
                            $nextID = $nextID['id'];
                            $status3->execute([':id' => $row['id'],':next'=>$nextID]);
                            $counters['deleted3']++;
                        } else {
                            $status4->execute([':id' => $row['id'],]);
                            $status4ForFather->execute([':next' => $row['id'],]);
                            $counters['deleted4']++;
                        }
                    }
                    else{
                        $counters['delayed']++;
                    }
                }
            }
        }
        catch(Throwable $exception){
            var_dump($row);
            print "Не удалось получить данные по заявке №" . $row['rosreestr_id'] . PHP_EOL;
            $counters['failure']++;
        }
    }
    print "Успешно " . $counters['success'] . PHP_EOL;
    print "Удалено по таймауту. Выставлен новый запрос " . $counters['deleted3'] . PHP_EOL;
    print "Удалено по таймауту " . $counters['deleted4'] . PHP_EOL;
    print "Выписка не готова " . $counters['delayed'] . PHP_EOL;
    print "Ошибка обработки " . $counters['failure'] . PHP_EOL;
    sleep(60*60*2);
}
