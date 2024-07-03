<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$origen = $datos['origen'];
$destino = $datos['destino'];
$fecha = $datos['fecha'];
$filtro = $datos['filtro'];

if(!$origen || !$destino || !$fecha || !$filtro){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->vuelos;

$consulta = array(
    'ubi_origen' => $origen,
    'ubi_destino' => $destino,
    'fecha' => $fecha
);

$vuelos = $coleccion->find($consulta);

$resultados = [];

foreach($vuelos as $vuelo){
    $resultados[] = [
        'id' => $vuelo['_id'],
        'nombre_empresa' => $vuelo['nombre_empresa'],
        'ubi_origen' => $vuelo['ubi_origen'],
        'ubi_destino' => $vuelo['ubi_destino'],
        'fecha' => $vuelo['fecha'],
        'hora_salida' => $vuelo['hora_salida'],
        'hora_llegada' => $vuelo['hora_llegada'],
        'precio' => $vuelo['precio'],
    ];
}

usort($resultados, function($a, $b) use ($filtro){
    if($filtro == 'precio_min'){
        return $a['precio'] <=> $b['precio'];
    }else if ($filtro == 'precio_max'){
        return $b['precio'] <=> $a['precio'];
    }else if ($filtro == 'hora_salida_temp'){
        return $a['hora_salida'] <=> $b['hora_salida'];
    }else if ($filtro == 'hora_salida_tarde'){
        return $b['hora_salida'] <=> $a['hora_salida'];
    }
}); 

echo json_encode($resultados);
exit;

?>


