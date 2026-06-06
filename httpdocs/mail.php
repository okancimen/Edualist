<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://www.edualist.com');
header('Access-Control-Allow-Methods: POST');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    $input = $_POST;
}

$type = isset($input['type']) ? $input['type'] : '';
$to   = 'okan@cimen.net';

function clean($val) {
    return htmlspecialchars(strip_tags(trim((string) $val)), ENT_QUOTES, 'UTF-8');
}

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

    $subject = "Edualist – New Consultation Request from {$name}";
    $body    = "New consultation request received from the Edualist website.\n\n"
             . "Name:        {$name}\n"
             . "Email:       {$email}\n"
             . "Phone:       {$phone}\n"
             . "Destination: {$relocation}\n"
             . "Details:\n{$details}\n";

} elseif ($type === 'webinar') {
    $name  = clean($input['name'] ?? '');
    $email = filter_var($input['email'] ?? '', FILTER_SANITIZE_EMAIL);
    $phone = clean($input['phone'] ?? '');

    if (!$name || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        http_response_code(400);
        echo json_encode(['ok' => false, 'error' => 'Invalid input']);
        exit;
    }

    $subject = "Edualist – Webinar Registration from {$name}";
    $body    = "New webinar registration received from the Edualist website.\n\n"
             . "Name:  {$name}\n"
             . "Email: {$email}\n"
             . "Phone: {$phone}\n";

} else {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Unknown form type']);
    exit;
}

$headers = "From: noreply@edualist.com\r\n"
         . "Reply-To: {$email}\r\n"
         . "X-Mailer: PHP/" . phpversion();

$sent = mail($to, $subject, $body, $headers);

if ($sent) {
    echo json_encode(['ok' => true]);
} else {
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'Mail delivery failed']);
}
