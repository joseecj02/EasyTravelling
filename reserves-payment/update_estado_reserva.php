<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$id_reserva = $datos['id_reserva'];
$estado = $datos['estado'];

if(!$id_reserva || !$estado){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$id_reserva = (int) $id_reserva;

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->reservas;

$consulta = array(
    '_id' => $id_reserva
);

$actualizacion = array(
    '$set' => array(
        'estado' => $estado
    )
);

$resultado = $coleccion->updateOne($consulta, $actualizacion);

?>