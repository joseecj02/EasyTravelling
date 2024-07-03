<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$ubicacion = $datos['ubicacion'];
$filtro = $datos['filtro'];


if(!$ubicacion || !$filtro){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->hotel;

$consulta = array(
    'ubicacion' => $ubicacion
);

$hoteles = $coleccion->find($consulta);

$resultados = [];

foreach($hoteles as $hotel){
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

usort($resultados, function($a, $b) use ($filtro){
    if($filtro == 'precio_min'){
        return $a['precio'] <=> $b['precio'];
    }else if ($filtro == 'precio_max'){
        return $b['precio'] <=> $a['precio'];
    }else if ($filtro == 'estrellas_min'){
        return $a['estrellas'] <=> $b['estrellas'];
    }else if ($filtro == 'estrellas_max'){
        return $b['estrellas'] <=> $a['estrellas'];
    }else if ($filtro == 'valoracion_min'){
        return $b['valoracion'] <=> $a['valoracion'];
    }else if ($filtro == 'estrellas_max'){
        return $b['valoracion'] <=> $a['valoracion'];
    }
}); 

echo json_encode($resultados);
exit;

?>


