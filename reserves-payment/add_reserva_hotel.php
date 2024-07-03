<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$id_hotel = $datos['id_hotel'];
$id_usuario = $datos['id_usuario'];
$precio = $datos['precio'];
$nombre = $datos['nombre'];
$estrellas = $datos['estrellas'];
$direccion = $datos['direccion'];
$fecha_llegada = $datos['fecha_llegada'];
$fecha_salida = $datos['fecha_salida'];
$ubicacion = $datos['ubicacion'];
$tipo_reserva = $datos['tipo_reserva'];
$estado = $datos['estado'];
$imagen = $datos['imagen'];

if(!$id_hotel || !$id_usuario || !$precio || !$nombre || !$estrellas || !$direccion || !$fecha_llegada || !$fecha_salida || !$ubicacion || !$tipo_reserva || !$estado || !$imagen){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$id_hotel = (int) $id_hotel;
$id_usuario = (int) $id_usuario;
$precio = (int) $precio;
$estrellas = (int) $estrellas;


$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->reservas;

$ultimaReserva = $coleccion->findOne([],['sort' => ['_id' => -1]]);

if($ultimaReserva){
    $ultimoId = $ultimaReserva['_id'];
    $nuevoId = $ultimoId + 1;
}else{
    $nuevoId = 1;
}

$consulta = array(
    '_id' => $nuevoId,
    'id_hotel' => $id_hotel,
    'id_usuario' => $id_usuario,
    'precio' => $precio,
    'nombre' => $nombre,
    'estrellas' => $estrellas,
    'direccion' => $direccion,
    'fecha_llegada' => $fecha_llegada,
    'fecha_salida' => $fecha_salida,
    'ubicacion' => $ubicacion,
    'tipo_reserva' => $tipo_reserva,
    'estado' => $estado,
    'imagen' => $imagen
);

$resultado = $coleccion->insertOne($consulta);

?>