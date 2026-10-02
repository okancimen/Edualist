<?php
define('CRON_TOKEN', '6c78cb816ceb781a029f39bb9d59ddd82574f03c84a09bac');

$token = isset($_GET['token']) ? $_GET['token'] : '';
if (!hash_equals(CRON_TOKEN, $token)) {
    http_response_code(403);
    exit('Forbidden');
}

$project_root = dirname(dirname(dirname(dirname(dirname(__DIR__)))));
$state_file   = $project_root . '/.index_state.json';

if (!file_exists($state_file)) {
    header('Content-Type: application/json');
    echo json_encode(array('status' => 'no_state', 'message' => 'No runs yet', 'state_file' => $state_file));
    exit;
}

$state     = json_decode(file_get_contents($state_file), true);
$submitted = $state['submitted'] ?? array();
$last_run  = $state['last_run_ts'] ?? 0;

arsort($submitted); // newest first

header('Content-Type: application/json');
echo json_encode(array(
    'last_run'       => $last_run ? date('Y-m-d H:i:s', $last_run) : 'never',
    'submitted_count' => count($submitted),
    'submitted'      => $submitted,
), JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
