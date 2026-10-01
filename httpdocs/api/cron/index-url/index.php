<?php
/**
 * Google Indexing API — cron endpoint
 * Cron URL: https://www.edualist.com/api/cron/index-url?token=CRON_TOKEN
 */

// ── Auth ──────────────────────────────────────────────────────────────────────

define('CRON_TOKEN', '6c78cb816ceb781a029f39bb9d59ddd82574f03c84a09bac');

$token = $_GET['token'] ?? $_SERVER['HTTP_X_CRON_TOKEN'] ?? '';
if (!hash_equals(CRON_TOKEN, $token)) {
    http_response_code(403);
    exit('Forbidden');
}

// ── Paths ─────────────────────────────────────────────────────────────────────
// __DIR__ = httpdocs/api/cron/index-url

$httpdocs     = dirname(dirname(dirname(__DIR__)));             // httpdocs/
$project_root = dirname($httpdocs);                            // one above httpdocs
$state_file   = $project_root . '/.index_state.json';
$key_file     = $project_root . '/private/aibot-service-account.json';
$base_url     = 'https://www.edualist.com';
$daily_limit  = 195;

// ── State ─────────────────────────────────────────────────────────────────────

$state     = file_exists($state_file)
    ? json_decode(file_get_contents($state_file), true)
    : ['last_run_ts' => 0, 'submitted' => []];
$since_ts  = (float)($state['last_run_ts'] ?? 0);
$submitted = $state['submitted'] ?? [];

// ── Find changed index.html files ─────────────────────────────────────────────

function html_to_url(string $path, string $httpdocs, string $base_url): string {
    $rel  = substr($path, strlen($httpdocs) + 1); // e.g. blog/foo/index.html
    $slug = dirname($rel);                         // e.g. blog/foo
    return ($slug === '.') ? "$base_url/" : "$base_url/$slug/";
}

$changed = [];
$iter = new RecursiveIteratorIterator(
    new RecursiveDirectoryIterator($httpdocs, FilesystemIterator::SKIP_DOTS)
);
foreach ($iter as $file) {
    if ($file->getFilename() !== 'index.html') continue;
    if ($file->getMTime() <= $since_ts) continue;
    $changed[] = [
        'url'   => html_to_url($file->getPathname(), $httpdocs, $base_url),
        'mtime' => $file->getMTime(),
    ];
}
usort($changed, fn($a, $b) => $b['mtime'] - $a['mtime']);
$changed = array_column($changed, 'url');

if (empty($changed)) {
    $state['last_run_ts'] = time();
    file_put_contents($state_file, json_encode($state, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    header('Content-Type: application/json');
    echo json_encode(['status' => 'ok', 'submitted' => 0, 'message' => 'No changes since last run']);
    exit;
}

if (count($changed) > $daily_limit) {
    $changed = array_slice($changed, 0, $daily_limit);
}

// ── Google OAuth — service account JWT → access token ────────────────────────

function base64url(string $data): string {
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

function get_access_token(string $key_file): string {
    if (!file_exists($key_file)) {
        throw new RuntimeException("Key file not found: $key_file");
    }
    $sa  = json_decode(file_get_contents($key_file), true);
    $now = time();

    $header = base64url(json_encode(['alg' => 'RS256', 'typ' => 'JWT']));
    $claims = base64url(json_encode([
        'iss'   => $sa['client_email'],
        'scope' => 'https://www.googleapis.com/auth/indexing',
        'aud'   => 'https://oauth2.googleapis.com/token',
        'exp'   => $now + 3600,
        'iat'   => $now,
    ]));

    $input = "$header.$claims";
    $key   = openssl_pkey_get_private($sa['private_key']);
    openssl_sign($input, $sig, $key, 'sha256WithRSAEncryption');
    $jwt = "$input." . base64url($sig);

    $ch = curl_init('https://oauth2.googleapis.com/token');
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query([
            'grant_type' => 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion'  => $jwt,
        ]),
        CURLOPT_RETURNTRANSFER => true,
    ]);
    $resp = json_decode(curl_exec($ch), true);
    curl_close($ch);

    if (empty($resp['access_token'])) {
        throw new RuntimeException('OAuth token exchange failed: ' . json_encode($resp));
    }
    return $resp['access_token'];
}

// ── Submit URLs ───────────────────────────────────────────────────────────────

$access_token = get_access_token($key_file);
$ok = $fail = 0;
$errors = [];

foreach ($changed as $url) {
    $ch = curl_init('https://indexing.googleapis.com/v3/urlNotifications:publish');
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => json_encode(['url' => $url, 'type' => 'URL_UPDATED']),
        CURLOPT_HTTPHEADER     => [
            'Content-Type: application/json',
            "Authorization: Bearer $access_token",
        ],
        CURLOPT_RETURNTRANSFER => true,
    ]);
    $body = curl_exec($ch);
    $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($code === 200) {
        $submitted[$url] = date('c');
        $ok++;
    } else {
        $errors[] = "$url → HTTP $code: $body";
        $fail++;
    }
    usleep(300000); // 300ms between requests
}

// ── Save state ────────────────────────────────────────────────────────────────

$state['last_run_ts'] = time();
$state['submitted']   = $submitted;
file_put_contents($state_file, json_encode($state, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

// ── Response ──────────────────────────────────────────────────────────────────

http_response_code($fail > 0 && $ok === 0 ? 500 : 200);
header('Content-Type: application/json');
echo json_encode([
    'status'    => $fail === 0 ? 'ok' : ($ok > 0 ? 'partial' : 'error'),
    'submitted' => $ok,
    'failed'    => $fail,
    'errors'    => $errors,
], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
