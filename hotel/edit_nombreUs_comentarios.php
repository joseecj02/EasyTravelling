<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$nombreUs = $datos['nombreUs'];
$id_usuario = $datos['id_usuario'];

if(!$nombreUs || !$id_usuario){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$id_usuario = (int) $id_usuario;

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->comentarios;

$cambiarnombreUs = ['id_usuario' => $id_usuario];
$actualizar = ['$set' => ['nombreUs' => $nombreUs]];

$resultado = $coleccion->updateMany($cambiarnombreUs, $actualizar);

?>
