<?php
/**
 * Google Indexing API — cron endpoint
 * Cron URL: https://www.edualist.com/api/cron/index-url?token=CRON_TOKEN
 */

error_reporting(E_ALL);
set_error_handler(function($severity, $message, $file, $line) {
    throw new ErrorException($message, 0, $severity, $file, $line);
});

// ── Auth ──────────────────────────────────────────────────────────────────────

define('CRON_TOKEN', '6c78cb816ceb781a029f39bb9d59ddd82574f03c84a09bac');

$token = isset($_GET['token']) ? $_GET['token'] : '';
if (!hash_equals(CRON_TOKEN, $token)) {
    http_response_code(403);
    exit('Forbidden');
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function html_to_url($path, $httpdocs, $base_url) {
    $rel  = substr($path, strlen($httpdocs) + 1);
    $slug = dirname($rel);
    return ($slug === '.') ? $base_url . '/' : $base_url . '/' . $slug . '/';
}

function base64url_enc($data) {
    return rtrim(strtr(base64_encode($data), '+/', '-_'), '=');
}

function get_access_token($key_file) {
    if (!file_exists($key_file)) {
        throw new RuntimeException('Key file not found: ' . $key_file);
    }
    $sa  = json_decode(file_get_contents($key_file), true);
    $now = time();

    $header = base64url_enc(json_encode(array('alg' => 'RS256', 'typ' => 'JWT')));
    $claims = base64url_enc(json_encode(array(
        'iss'   => $sa['client_email'],
        'scope' => 'https://www.googleapis.com/auth/indexing',
        'aud'   => 'https://oauth2.googleapis.com/token',
        'exp'   => $now + 3600,
        'iat'   => $now,
    )));

    $input = $header . '.' . $claims;
    $key   = openssl_pkey_get_private($sa['private_key']);
    openssl_sign($input, $sig, $key, 'sha256WithRSAEncryption');
    $jwt = $input . '.' . base64url_enc($sig);

    $ch = curl_init('https://oauth2.googleapis.com/token');
    curl_setopt_array($ch, array(
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => http_build_query(array(
            'grant_type' => 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion'  => $jwt,
        )),
        CURLOPT_RETURNTRANSFER => true,
    ));
    $resp = json_decode(curl_exec($ch), true);
    curl_close($ch);

    if (empty($resp['access_token'])) {
        throw new RuntimeException('OAuth failed: ' . json_encode($resp));
    }
    return $resp['access_token'];
}

// ── Main ──────────────────────────────────────────────────────────────────────

try {

    // Paths
    // __DIR__ = httpdocs/api/cron/index-url
    $httpdocs     = dirname(dirname(dirname(__DIR__)));
    $project_root = dirname($httpdocs);
    $state_file   = $project_root . '/.index_state.json';
    $key_file     = $project_root . '/private/aibot-service-account.json';
    $base_url     = 'https://www.edualist.com';
    $daily_limit  = 195;
    $time_limit   = 25; // stop after 25s so panel doesn't time out
    $start_time   = time();

    // State
    $state     = file_exists($state_file)
        ? json_decode(file_get_contents($state_file), true)
        : array('last_run_ts' => 0, 'submitted' => array());
    $since_ts  = (float)$state['last_run_ts'];
    $submitted = $state['submitted'];

    // Find changed index.html files
    $changed = array();
    $iter = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($httpdocs, FilesystemIterator::SKIP_DOTS)
    );
    foreach ($iter as $file) {
        if ($file->getFilename() !== 'index.html') continue;
        if ($file->getMTime() <= $since_ts) continue;
        $changed[] = array(
            'url'   => html_to_url($file->getPathname(), $httpdocs, $base_url),
            'mtime' => $file->getMTime(),
        );
    }
    usort($changed, function($a, $b) { return $b['mtime'] - $a['mtime']; });
    $urls = array();
    foreach ($changed as $item) { $urls[] = $item['url']; }

    if (empty($urls)) {
        $state['last_run_ts'] = time();
        file_put_contents($state_file, json_encode($state, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        header('Content-Type: application/json');
        echo json_encode(array('status' => 'ok', 'submitted' => 0, 'message' => 'No changes since last run'));
        exit;
    }

    if (count($urls) > $daily_limit) {
        $urls = array_slice($urls, 0, $daily_limit);
    }

    // Submit
    $access_token = get_access_token($key_file);
    $ok = 0; $fail = 0; $errors = array();

    foreach ($urls as $url) {
        $ch = curl_init('https://indexing.googleapis.com/v3/urlNotifications:publish');
        curl_setopt_array($ch, array(
            CURLOPT_POST           => true,
            CURLOPT_POSTFIELDS     => json_encode(array('url' => $url, 'type' => 'URL_UPDATED')),
            CURLOPT_HTTPHEADER     => array(
                'Content-Type: application/json',
                'Authorization: Bearer ' . $access_token,
            ),
            CURLOPT_RETURNTRANSFER => true,
        ));
        $body = curl_exec($ch);
        $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($code === 200) {
            $submitted[$url] = date('c');
            $ok++;
        } else {
            $errors[] = $url . ' -> HTTP ' . $code . ': ' . $body;
            $fail++;
        }
        usleep(100000); // 100ms between requests
        if ((time() - $start_time) >= $time_limit) break; // save state and exit before panel timeout
    }

    // Save state — only advance timestamp if all URLs were processed
    $timed_out = (time() - $start_time) >= $time_limit;
    if (!$timed_out) { $state['last_run_ts'] = time(); }
    $state['submitted'] = $submitted;
    file_put_contents($state_file, json_encode($state, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

    // Response
    $status = $fail === 0 ? 'ok' : ($ok > 0 ? 'partial' : 'error');
    if ($timed_out) { $status = 'partial_timeout'; }
    http_response_code(200);
    header('Content-Type: application/json');
    echo json_encode(array(
        'status'    => $status,
        'submitted' => $ok,
        'failed'    => $fail,
        'timed_out' => $timed_out,
        'errors'    => $errors,
    ), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);

} catch (Exception $e) {
    http_response_code(500);
    header('Content-Type: application/json');
    $httpdocs     = isset($httpdocs)     ? $httpdocs     : dirname(dirname(dirname(__DIR__)));
    $project_root = isset($project_root) ? $project_root : dirname($httpdocs);
    $key_file     = isset($key_file)     ? $key_file     : $project_root . '/private/aibot-service-account.json';
    echo json_encode(array(
        'status'    => 'error',
        'message'   => $e->getMessage(),
        'paths'     => array(
            '__DIR__'      => __DIR__,
            'httpdocs'     => $httpdocs,
            'project_root' => $project_root,
            'key_file'     => $key_file,
            'key_exists'   => file_exists($key_file),
        ),
    ), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
}
