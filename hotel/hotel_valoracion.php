<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->hotel;

$orden = ['valoracion' => -1];
$limite = 10;

$hoteles = $coleccion->find([], ['limit' => $limite, 'sort' => $orden]);

$resultados = [];

foreach ($hoteles as $hotel){
    $resultados[] = [
        'id' => $hotel['_id'],
        'nombre' => $hotel['nombre'],
        'ubicacion' => $hotel['ubicacion'],
        'descripcion' => $hotel['descripcion'],
        'valoracion' => $hotel['valoracion'],
        'precio' => $hotel['precio'],
        'estrellas' => $hotel['estrellas'],
        'imagen' => $hotel['imagen'],
        'telefono' => $hotel['telefono'],
        'direccion' => $hotel['direccion']
    ];
}

echo json_encode($resultados);
exit;

?>