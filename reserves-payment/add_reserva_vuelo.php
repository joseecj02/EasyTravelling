<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$id_vuelo = $datos['id_vuelo'];
$id_usuario = $datos['id_usuario'];
$precio = $datos['precio'];
$nombre_empresa = $datos['nombre_empresa'];
$origen = $datos['origen'];
$destino = $datos['destino'];
$fecha = $datos['fecha'];
$hora_salida = $datos['hora_salida'];
$hora_llegada = $datos['hora_llegada'];
$tipo_reserva = $datos['tipo_reserva'];
$estado = $datos['estado'];

if(!$id_vuelo || !$id_usuario || !$precio || !$nombre_empresa || !$origen || !$destino || !$fecha || !$hora_llegada || !$hora_salida|| !$tipo_reserva || !$estado){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$id_vuelo = (int) $id_vuelo;
$id_usuario = (int) $id_usuario;
$precio = (int) $precio;


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
    'id_vuelo' => $id_vuelo,
    'id_usuario' => $id_usuario,
    'precio' => $precio,
    'nombre_empresa' => $nombre_empresa,
    'origen' => $origen,
    'destino' => $destino,
    'hora_salida' => $hora_salida,
    'hora_llegada' => $hora_llegada,
    'fecha' => $fecha,
    'tipo_reserva' => $tipo_reserva,
    'estado' => $estado
);

$resultado = $coleccion->insertOne($consulta);

?>