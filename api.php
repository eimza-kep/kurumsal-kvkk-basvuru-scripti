<?php
/**
 * api.php
 * -------
 * 6698 KVKK İlgili Kişi Başvurusu PHP Uç Noktası (cPanel / Apache / Nginx uyumlu).
 * Verileri yerel 'kvkk_submissions.json' dosyasında güvenle saklar.
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$dataFile = __DIR__ . '/kvkk_submissions.json';

if (!file_exists($dataFile)) {
    file_put_contents($dataFile, json_encode([], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

$action = $_GET['action'] ?? '';

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $content = file_get_contents($dataFile);
    echo $content ?: '[]';
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    if (!$input) {
        http_response_code(400);
        echo json_encode(['error' => 'Geçersiz veri gönderildi.']);
        exit;
    }

    $currentData = json_decode(file_get_contents($dataFile), true) ?: [];
    $trackingCode = 'KVKK-' . date('Y') . '-' . rand(100000, 999999);

    $entry = [
        'id' => count($currentData) + 1,
        'tracking_code' => $trackingCode,
        'full_name' => htmlspecialchars($input['full_name'] ?? ''),
        'id_number' => htmlspecialchars($input['id_number'] ?? ''),
        'phone' => htmlspecialchars($input['phone'] ?? ''),
        'email' => htmlspecialchars($input['email'] ?? ''),
        'relationship' => htmlspecialchars($input['relationship'] ?? ''),
        'address' => htmlspecialchars($input['address'] ?? ''),
        'rights' => $input['rights'] ?? [],
        'details' => htmlspecialchars($input['details'] ?? ''),
        'response_channel' => htmlspecialchars($input['response_channel'] ?? ''),
        'kep_address' => htmlspecialchars($input['kep_address'] ?? ''),
        'status' => 'İnceleniyor',
        'created_at' => date('c')
    ];

    $currentData[] = $entry;
    file_put_contents($dataFile, json_encode($currentData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

    echo json_encode([
        'success' => true,
        'tracking_code' => $trackingCode,
        'message' => 'KVKK başvurunuz başarıyla kaydedilmiştir.'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}
?>
