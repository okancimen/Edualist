<?php
ob_start();
error_reporting(0);
ini_set('display_errors', 0);
header('Content-Type: application/json');

require_once __DIR__ . '/mail-config.php';

function jsonOut($ok, $error = '') {
    ob_clean();
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    jsonOut(false, 'Method not allowed');
}

$raw   = file_get_contents('php://input');
$input = json_decode($raw, true);
if (!$input) { parse_str($raw, $input); }
if (!$input) { $input = $_POST; }

$type = isset($input['type']) ? (string)$input['type'] : '';

function cl($v) {
    return htmlspecialchars(strip_tags(trim((string)$v)), ENT_QUOTES, 'UTF-8');
}

if ($type === 'consultation') {
    $name  = cl(isset($input['name'])       ? $input['name']       : '');
    $email = filter_var(isset($input['email']) ? $input['email'] : '', FILTER_SANITIZE_EMAIL);
    $phone = cl(isset($input['phone'])      ? $input['phone']      : '');
    $dest  = cl(isset($input['relocation']) ? $input['relocation'] : '');
    $det   = cl(isset($input['details'])    ? $input['details']    : '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        jsonOut(false, 'Invalid input');
    }

    $subject = "Edualist - Yeni Danismanlik Talebi: " . $name;
    $body    = "Yeni danismanlik talebi:\n\nAd Soyad:   $name\nE-posta:    $email\nTelefon:    $phone\nHedef Ulke: $dest\n\nDetaylar:\n$det";

} elseif ($type === 'webinar') {
    $name  = cl(isset($input['name'])  ? $input['name']  : '');
    $email = filter_var(isset($input['email']) ? $input['email'] : '', FILTER_SANITIZE_EMAIL);
    $phone = cl(isset($input['phone']) ? $input['phone'] : '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        jsonOut(false, 'Invalid input');
    }

    $subject = "Edualist - Webinar Kaydi: " . $name;
    $body    = "Yeni webinar kaydi:\n\nAd Soyad: $name\nE-posta:  $email\nTelefon:  $phone";

} else {
    jsonOut(false, 'Unknown type');
}

// SMTP over SSL (port 465)
function smtpSend($subject, $body, $replyTo) {
    $host = SMTP_HOST;
    $port = SMTP_PORT;
    $user = SMTP_USER;
    $pass = SMTP_PASS;
    $from = SMTP_FROM;
    $to   = MAIL_TO;

    $ctx = stream_context_create(['ssl' => [
        'verify_peer'       => false,
        'verify_peer_name'  => false,
        'allow_self_signed' => true,
    ]]);

    $socket = @stream_socket_client(
        "ssl://{$host}:{$port}", $errno, $errstr, 15, STREAM_CLIENT_CONNECT, $ctx
    );

    if (!$socket) { return false; }

    stream_set_timeout($socket, 15);

    function smtpRead($s) {
        $r = '';
        while ($line = fgets($s, 512)) {
            $r .= $line;
            if (substr($line, 3, 1) === ' ') break;
        }
        return $r;
    }

    function smtpSend2($s, $cmd) {
        fwrite($s, $cmd . "\r\n");
        return smtpRead($s);
    }

    smtpRead($socket); // banner

    $resp = smtpSend2($socket, "EHLO edualist.com");
    if ((int)$resp !== 250 && strpos($resp, '250') === false) {
        fclose($socket); return false;
    }

    smtpSend2($socket, "AUTH LOGIN");
    smtpSend2($socket, base64_encode($user));
    $resp = smtpSend2($socket, base64_encode($pass));
    if (strpos($resp, '235') === false) { fclose($socket); return false; }

    smtpSend2($socket, "MAIL FROM:<{$from}>");
    smtpSend2($socket, "RCPT TO:<{$to}>");
    smtpSend2($socket, "DATA");

    $msg  = "From: Edualist <{$from}>\r\n";
    $msg .= "To: <{$to}>\r\n";
    $msg .= "Reply-To: {$replyTo}\r\n";
    $msg .= "Subject: =?UTF-8?B?" . base64_encode($subject) . "?=\r\n";
    $msg .= "MIME-Version: 1.0\r\n";
    $msg .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $msg .= "Content-Transfer-Encoding: base64\r\n";
    $msg .= "\r\n";
    $msg .= chunk_split(base64_encode($body));
    $msg .= "\r\n.";

    $resp = smtpSend2($socket, $msg);
    smtpSend2($socket, "QUIT");
    fclose($socket);

    return strpos($resp, '250') !== false;
}

$sent = smtpSend($subject, $body, $email);

if ($sent) {
    jsonOut(true);
} else {
    error_log("[Edualist] SMTP failed. type={$type} from={$email}");
    jsonOut(false, 'Mail delivery failed');
}
