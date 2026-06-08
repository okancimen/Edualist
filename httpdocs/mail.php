<?php
ob_start();
error_reporting(0);
ini_set('display_errors', 0);
header('Content-Type: application/json');

function jsonOut($ok, $error = '') {
    ob_clean();
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    jsonOut(false, 'Method not allowed');
}

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) { $input = $_POST; }

$type = isset($input['type']) ? $input['type'] : '';

function clean($val) {
    return htmlspecialchars(strip_tags(trim((string) $val)), ENT_QUOTES, 'UTF-8');
}

$to = 'okan@cimen.net';

if ($type === 'consultation') {
    $name       = clean($input['name'] ?? '');
    $email      = filter_var($input['email'] ?? '', FILTER_SANITIZE_EMAIL);
    $phone      = clean($input['phone'] ?? '');
    $relocation = clean($input['relocation'] ?? '');
    $details    = clean($input['details'] ?? '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        jsonOut(false, 'Invalid input');
    }

    $subject = "Edualist – Yeni Danışmanlık Talebi: {$name}";
    $body    = "Yeni danışmanlık talebi:\n\n"
             . "Ad Soyad:   {$name}\n"
             . "E-posta:    {$email}\n"
             . "Telefon:    {$phone}\n"
             . "Hedef Ülke: {$relocation}\n\n"
             . "Detaylar:\n{$details}\n";

} elseif ($type === 'webinar') {
    $name  = clean($input['name'] ?? '');
    $email = filter_var($input['email'] ?? '', FILTER_SANITIZE_EMAIL);
    $phone = clean($input['phone'] ?? '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        jsonOut(false, 'Invalid input');
    }

    $subject = "Edualist – Webinar Kaydı: {$name}";
    $body    = "Yeni webinar kaydı:\n\n"
             . "Ad Soyad: {$name}\n"
             . "E-posta:  {$email}\n"
             . "Telefon:  {$phone}\n";

} else {
    jsonOut(false, 'Unknown form type');
}

$headers  = "From: Edualist <noreply@edualist.com>\r\n";
$headers .= "Reply-To: {$email}\r\n";
$headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$headers .= "MIME-Version: 1.0\r\n";

$sent = @mail($to, $subject, $body, $headers, '-f noreply@edualist.com');

if ($sent) {
    jsonOut(true);
} else {
    error_log("[Edualist] mail() failed. type={$type} from={$email}");
    jsonOut(false, 'Mail delivery failed');
}
