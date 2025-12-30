<?php
header("Content-Type: application/json");
$conn = new mysqli("localhost", "root", "", "trading_db");

if ($conn->connect_error) die(json_encode(["error" => "Connection failed"]));

$action = $_GET['action'] ?? '';

if ($action == 'read') {
    $result = $conn->query("SELECT * FROM journal_entries ORDER BY id DESC");
    echo json_encode($result->fetch_all(MYSQLI_ASSOC));
}

if ($action == 'save') {
    $data = json_decode(file_get_contents("php://input"), true);
    // Check if updating or creating
    $check = $conn->query("SELECT id FROM journal_entries WHERE id = {$data['id']}");
    
    $mistakes = json_encode($data['mistakes'] ?? []);
    $images = json_encode($data['images'] ?? []);

    if ($check->num_rows > 0) {
        $stmt = $conn->prepare("UPDATE journal_entries SET asset=?, focus_area=?, notes=?, mistakes=?, neg_notes=?, plan_bias=?, key_level=?, plan_notes=?, images=? WHERE id=?");
        $stmt->bind_param("sssssssssi", $data['asset'], $data['area'], $data['notes'], $mistakes, $data['negNotes'], $data['bias'], $data['level'], $data['planNotes'], $images, $data['id']);
    } else {
        $stmt = $conn->prepare("INSERT INTO journal_entries (id, entry_type, asset, timestamp_str, focus_area, notes, mistakes, neg_notes, plan_bias, key_level, plan_notes, images) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
        $stmt->bind_param("isssssssssss", $data['id'], $data['type'], $data['asset'], $data['timestamp'], $data['area'], $data['notes'], $mistakes, $data['negNotes'], $data['bias'], $data['level'], $data['planNotes'], $images);
    }
    $stmt->execute();
    echo json_encode(["success" => true]);
}

if ($action == 'delete') {
    $id = $_GET['id'];
    $conn->query("DELETE FROM journal_entries WHERE id = $id");
    echo json_encode(["success" => true]);
}
?>