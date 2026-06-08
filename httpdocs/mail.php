<?php
error_reporting(0);
ini_set('display_errors', 0);
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) { $input = $_POST; }

$type = isset($input['type']) ? $input['type'] : '';

function clean($val) {
    return htmlspecialchars(strip_tags(trim((string) $val)), ENT_QUOTES, 'UTF-8');
}

function sendSmtp($to, $subject, $body, $fromEmail, $fromName, $replyTo) {
    $host     = 'localhost';
    $port     = 25;
    $timeout  = 10;

    $socket = @fsockopen($host, $port, $errno, $errstr, $timeout);
    if (!$socket) { return false; }

    $boundary = md5(uniqid());

    $message  = "Date: " . date('r') . "\r\n";
    $message .= "From: =?UTF-8?B?" . base64_encode($fromName) . "?= <{$fromEmail}>\r\n";
    $message .= "Reply-To: {$replyTo}\r\n";
    $message .= "To: {$to}\r\n";
    $message .= "Subject: =?UTF-8?B?" . base64_encode($subject) . "?=\r\n";
    $message .= "MIME-Version: 1.0\r\n";
    $message .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $message .= "Content-Transfer-Encoding: base64\r\n";
    $message .= "\r\n";
    $message .= chunk_split(base64_encode($body));

    $domain = gethostname() ?: 'edualist.com';

    $steps = [
        "EHLO {$domain}\r\n",
        "MAIL FROM:<{$fromEmail}>\r\n",
        "RCPT TO:<{$to}>\r\n",
        "DATA\r\n",
        $message . "\r\n.\r\n",
        "QUIT\r\n",
    ];

    fgets($socket, 512); // banner
    foreach ($steps as $i => $cmd) {
        fwrite($socket, $cmd);
        $response = fgets($socket, 512);
        $code = (int) substr($response, 0, 3);
        // DATA command expects 354, others expect 2xx
        if ($i === 3 && $code !== 354) { fclose($socket); return false; }
        if ($i !== 3 && $code >= 400)  { fclose($socket); return false; }
    }

    fclose($socket);
    return true;
}

$toAddress = 'okan@cimen.net';

if ($type === 'consultation') {
    $name       = clean($input['name'] ?? '');
    $email      = filter_var($input['email'] ?? '', FILTER_SANITIZE_EMAIL);
    $phone      = clean($input['phone'] ?? '');
    $relocation = clean($input['relocation'] ?? '');
    $details    = clean($input['details'] ?? '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Invalid input']);
        exit;
    }

    $subject = "Edualist – Yeni Danışmanlık Talebi: {$name}";
    $body    = "Edualist web sitesinden yeni bir danışmanlık talebi alındı.\n\n"
             . "Ad Soyad:    {$name}\n"
             . "E-posta:     {$email}\n"
             . "Telefon:     {$phone}\n"
             . "Hedef Ülke:  {$relocation}\n\n"
             . "Detaylar:\n{$details}\n";

} elseif ($type === 'webinar') {
    $name  = clean($input['name'] ?? '');
    $email = filter_var($input['email'] ?? '', FILTER_SANITIZE_EMAIL);
    $phone = clean($input['phone'] ?? '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Invalid input']);
        exit;
    }

    $subject = "Edualist – Webinar Kaydı: {$name}";
    $body    = "Edualist web sitesinden yeni bir webinar kaydı alındı.\n\n"
             . "Ad Soyad: {$name}\n"
             . "E-posta:  {$email}\n"
             . "Telefon:  {$phone}\n";

} else {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Unknown form type']);
    exit;
}

$fromEmail = 'noreply@edualist.com';
$fromName  = 'Edualist';
$replyTo   = $email;

// Try SMTP first, fall back to mail()
$sent = sendSmtp($toAddress, $subject, $body, $fromEmail, $fromName, $replyTo);
if (!$sent) {
    $headers  = "From: Edualist <{$fromEmail}>\r\n";
    $headers .= "Reply-To: {$replyTo}\r\n";
    $headers .= "MIME-Version: 1.0\r\n";
    $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $sent = @mail($toAddress, $subject, $body, $headers);
}

if (!$sent) {
    error_log("[Edualist mail.php] Both SMTP and mail() failed. type={$type} from={$email}");
    echo json_encode(['ok' => false, 'error' => 'Mail delivery failed']);
    exit;
}

echo json_encode(['ok' => true]);
