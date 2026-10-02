<?php
define('CRON_TOKEN', '6c78cb816ceb781a029f39bb9d59ddd82574f03c84a09bac');

$token = isset($_GET['token']) ? $_GET['token'] : '';
if (!hash_equals(CRON_TOKEN, $token)) {
    http_response_code(403);
    exit('Forbidden');
}

header('Content-Type: application/json');

try {
    // __DIR__ = httpdocs/api/cron/index-url/status
    $project_root = dirname(dirname(dirname(dirname(dirname(__DIR__)))));
    $state_file   = $project_root . '/.index_state.json';

    if (!file_exists($state_file)) {
        echo json_encode(array(
            'status'     => 'no_state',
            'message'    => 'No runs yet — state file not found',
            'state_file' => $state_file,
            '__dir__'    => __DIR__,
        ), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        exit;
    }

    $raw   = file_get_contents($state_file);
    $state = json_decode($raw, true);

    if (!is_array($state)) {
        echo json_encode(array('status' => 'error', 'message' => 'State file is not valid JSON', 'raw' => $raw));
        exit;
    }

    $submitted = isset($state['submitted']) ? $state['submitted'] : array();
    $last_run  = isset($state['last_run_ts']) ? $state['last_run_ts'] : 0;

    arsort($submitted);

    echo json_encode(array(
        'last_run'        => $last_run ? date('Y-m-d H:i:s T', (int)$last_run) : 'never',
        'submitted_count' => count($submitted),
        'submitted'       => $submitted,
    ), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(array(
        'status'  => 'error',
        'message' => $e->getMessage(),
        '__dir__' => __DIR__,
    ), JSON_PRETTY_PRINT);
}
