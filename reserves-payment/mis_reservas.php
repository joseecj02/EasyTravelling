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

$coleccion = $db->reservas;

$consulta = array(
    'id_usuario' => $id_usuario
);

$reservas = $coleccion->find($consulta);

$resultados = [];

foreach($reservas as $reserva){
    if($reserva['tipo_reserva'] == 'Hotel'){
        $resultados[] = [
            'id' => $reserva['_id'],
            'id_hotel' => $reserva['id_hotel'],
            'precio' => $reserva['precio'],
            'nombre' => $reserva['nombre'],
            'estrellas' => $reserva['estrellas'],
            'direccion' => $reserva['direccion'],
            'fecha_llegada' => $reserva['fecha_llegada'],
            'fecha_salida' => $reserva['fecha_salida'],
            'ubicacion' => $reserva['ubicacion'],
            'tipo_reserva' => $reserva['tipo_reserva'],
            'estado' => $reserva['estado'],
            'imagen' => $reserva['imagen']
        ];

    }else if($reserva['tipo_reserva'] == 'Vuelo'){
        $resultados[] = [
            'id' => $reserva['_id'],
            'id_vuelo' => $reserva['id_vuelo'],
            'precio' => $reserva['precio'],
            'nombre_empresa' => $reserva['nombre_empresa'],
            'origen' => $reserva['origen'],
            'destino' => $reserva['destino'],
            'hora_salida' => $reserva['hora_salida'],
            'hora_llegada' => $reserva['hora_llegada'],
            'fecha' => $reserva['fecha'],
            'tipo_reserva' => $reserva['tipo_reserva'],
            'estado' => $reserva['estado']
        ];
    }else if($reserva['tipo_reserva'] == 'Bus'){
        $resultados[] = [
            'id' => $reserva['_id'],
            'id_bus' => $reserva['id_bus'],
            'precio' => $reserva['precio'],
            'nombre_empresa' => $reserva['nombre_empresa'],
            'origen' => $reserva['origen'],
            'destino' => $reserva['destino'],
            'hora_salida' => $reserva['hora_salida'],
            'hora_llegada' => $reserva['hora_llegada'],
            'fecha' => $reserva['fecha'],
            'tipo_reserva' => $reserva['tipo_reserva'],
            'estado' => $reserva['estado'],
        ];
    }

    usort($resultados, function ($a, $b) {
        if ($a['tipo_reserva'] == 'Hotel') {
            $fechaA = $a['fecha_llegada'];
        } else {
            $fechaA = $a['fecha'];
        }
    
        if ($b['tipo_reserva'] == 'Hotel') {
            $fechaB = $b['fecha_llegada'];
        } else {
            $fechaB = $b['fecha'];
        }
    
        return strtotime($fechaB) - strtotime($fechaA);
    });
}

echo json_encode($resultados);
exit;

?>