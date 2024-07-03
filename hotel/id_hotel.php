<?php

require_once 'Conexion.php';

header('Content-Type: application/json; charset=UTF-8');

$datos = json_decode(file_get_contents('php://input'), true);

$nombre = $datos['nombre'];


if(!$nombre){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->hotel;

$consulta = array(
    'nombre' => $nombre
);

$hoteles = $coleccion->find($consulta);

$resultados = [];

foreach($hoteles as $hotel){
    $resultados[] = [
        'id' => $hotel['_id']
    ];
}

echo json_encode($resultados);
exit;

?>