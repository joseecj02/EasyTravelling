<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$id_usuario = $datos['id_usuario'];

if(!$id_usuario){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$id_usuario = (int) $id_usuario;

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->comentarios;

$resultado = $coleccion->deleteMany(['id_usuario' => $id_usuario]);
