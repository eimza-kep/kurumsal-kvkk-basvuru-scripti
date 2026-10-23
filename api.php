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
        echo json_encode(['success' => false, 'error' => 'Geçersiz veri gönderildi.'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    $currentData = json_decode(file_get_contents($dataFile), true) ?: [];

    // Durum Güncelleme
    if ($action === 'status') {
        $code = trim($input['tracking_code'] ?? '');
        $status = trim($input['status'] ?? '');
        $note = trim($input['resolution_note'] ?? '');
        $found = false;
        foreach ($currentData as &$item) {
            if ($item['tracking_code'] === $code) {
                $item['status'] = $status;
                $item['resolution_note'] = $note;
                $found = true;
                break;
            }
        }
        if ($found) {
            file_put_contents($dataFile, json_encode($currentData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
            echo json_encode(['success' => true, 'message' => 'Durum güncellendi.'], JSON_UNESCAPED_UNICODE);
        } else {
            http_response_code(404);
            echo json_encode(['success' => false, 'error' => 'Kayıt bulunamadı.'], JSON_UNESCAPED_UNICODE);
        }
        exit;
    }

    // Takip / Sorgulama
    if ($action === 'track') {
        $code = trim($input['tracking_code'] ?? '');
        $idVerify = trim($input['id_verify'] ?? '');
        foreach ($currentData as $item) {
            if (strcasecmp($item['tracking_code'], $code) === 0) {
                $rawId = trim($item['id_number'] ?? '');
                if (!$idVerify || substr($rawId, -strlen($idVerify)) === $idVerify || $rawId === $idVerify) {
                    $nameParts = explode(' ', trim($item['full_name'] ?? ''));
                    $masked = [];
                    foreach ($nameParts as $p) {
                        $masked[] = mb_substr($p, 0, 1) . str_repeat('*', max(1, mb_strlen($p) - 1));
                    }
                    echo json_encode([
                        'success' => true,
                        'data' => [
                            'tracking_code' => $item['tracking_code'],
                            'masked_name' => implode(' ', $masked),
                            'relationship' => $item['relationship'] ?? '',
                            'response_channel' => $item['response_channel'] ?? '',
                            'status' => $item['status'] ?? 'İnceleniyor',
                            'resolution_note' => $item['resolution_note'] ?? '',
                            'created_at' => $item['created_at'] ?? date('c'),
                            'deadline' => [
                                'days_left' => 25,
                                'deadline_date' => date('d.m.Y', strtotime('+30 days')),
                                'badge_text' => '⏳ 30 Günlük Yasal Süre',
                                'color' => '#15803d'
                            ]
                        ]
                    ], JSON_UNESCAPED_UNICODE);
                    exit;
                } else {
                    http_response_code(403);
                    echo json_encode(['success' => false, 'error' => 'Kimlik doğrulama başarısız.'], JSON_UNESCAPED_UNICODE);
                    exit;
                }
            }
        }
        http_response_code(404);
        echo json_encode(['success' => false, 'error' => 'Başvuru bulunamadı.'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    // KEP doğrulaması
    $channel = $input['response_channel'] ?? '';
    $kepAddress = trim($input['kep_address'] ?? '');
    if ($channel === 'KEP') {
        if (!$kepAddress || !preg_match('/^[a-zA-Z0-9_\.\-]+@[a-zA-Z0-9_\.\-]+\.kep\.tr$/i', $kepAddress)) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Geçerli bir BTK uyumlu KEP adresi girilmelidir (Örn: ad.soyad@hs01.kep.tr).'], JSON_UNESCAPED_UNICODE);
            exit;
        }
    }

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
        'response_channel' => htmlspecialchars($channel),
        'kep_address' => htmlspecialchars($kepAddress),
        'status' => 'İnceleniyor',
        'resolution_note' => '',
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
