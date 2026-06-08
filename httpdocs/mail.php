<?php
ob_start();
error_reporting(0);
ini_set('display_errors', 0);
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    ob_clean(); echo '{}'; exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    ob_clean(); echo json_encode(['ok' => false, 'error' => 'Method not allowed']); exit;
}

$raw   = file_get_contents('php://input');
$input = json_decode($raw, true);
if (!$input) { parse_str($raw, $input); }
if (!$input) { $input = $_POST; }

$type = isset($input['type']) ? (string)$input['type'] : '';

function cl($v) {
    return htmlspecialchars(strip_tags(trim((string)$v)), ENT_QUOTES, 'UTF-8');
}

$to = 'okan@cimen.net';

if ($type === 'consultation') {
    $name  = cl(isset($input['name'])  ? $input['name']  : '');
    $email = filter_var(isset($input['email']) ? $input['email'] : '', FILTER_SANITIZE_EMAIL);
    $phone = cl(isset($input['phone']) ? $input['phone'] : '');
    $dest  = cl(isset($input['relocation']) ? $input['relocation'] : '');
    $det   = cl(isset($input['details']) ? $input['details'] : '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        ob_clean(); echo json_encode(['ok' => false, 'error' => 'Invalid input']); exit;
    }

    $subject = "Edualist - Yeni Danismanlik Talebi: " . $name;
    $body    = "Yeni danismanlik talebi:\n\nAd: $name\nEmail: $email\nTelefon: $phone\nHedef: $dest\n\nDetay:\n$det";

} elseif ($type === 'webinar') {
    $name  = cl(isset($input['name'])  ? $input['name']  : '');
    $email = filter_var(isset($input['email']) ? $input['email'] : '', FILTER_SANITIZE_EMAIL);
    $phone = cl(isset($input['phone']) ? $input['phone'] : '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        ob_clean(); echo json_encode(['ok' => false, 'error' => 'Invalid input']); exit;
    }

    $subject = "Edualist - Webinar Kaydi: " . $name;
    $body    = "Yeni webinar kaydi:\n\nAd: $name\nEmail: $email\nTelefon: $phone";

} else {
    ob_clean(); echo json_encode(['ok' => false, 'error' => 'Unknown type']); exit;
}

$headers = "From: noreply@edualist.com\r\nReply-To: " . $email . "\r\nContent-Type: text/plain; charset=UTF-8\r\n";

$sent = @mail($to, $subject, $body, $headers);

ob_clean();
echo json_encode(['ok' => true, 'sent' => $sent]);
