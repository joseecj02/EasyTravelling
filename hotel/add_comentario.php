<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$id_hotel = $datos['id_hotel'];
$id_usuario = $datos['id_usuario'];
$nombreUs = $datos['nombreUs'];
$comentario = $datos['comentario'];
$valoracion = $datos['valoracion'];
$fechaPubli = $datos['fechaPubli'];

if(!$id_hotel || !$id_usuario || !$nombreUs || !$comentario || !$valoracion || !$fechaPubli){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$id_hotel = (int) $id_hotel;
$id_usuario = (int) $id_usuario;
$valoracion = (int) $valoracion;

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->comentarios;

$ultimoComentario = $coleccion->findOne([],['sort' => ['_id' => -1]]);

if($ultimoComentario){
    $ultimoId = $ultimoComentario['_id'];
    $nuevoId = $ultimoId + 1;
}else{
    $nuevoId = 1;
}

$consulta = array(
    '_id' => $nuevoId,
    'id_hotel' => $id_hotel,
    'id_usuario' => $id_usuario,
    'nombreUs' => $nombreUs,
    'comentario' => $comentario,
    'valoracion' => $valoracion,
    'fechaPubli' => $fechaPubli
);

$resultado = $coleccion->insertOne($consulta);

$coleccion_valoracion = $db->hotel;
$consulta_valoracion = array(
    '_id' => $id_hotel
);

$hotel = $coleccion_valoracion->findOne($consulta_valoracion);
$hotelArray = $hotel ? (array)$hotel : null;

if($hotelArray){
    $nueva_valoracion_total = $hotelArray['ValoracionesTotal'] + $valoracion;
    $nuevo_numValoraciones = $hotelArray['numValoraciones'] + 1;
    $nueva_valoracion = round($nueva_valoracion_total / $nuevo_numValoraciones, 1);

    $actualizacion = array(
        '$set' => array(
            'ValoracionesTotal' => $nueva_valoracion_total,
            'numValoraciones' => $nuevo_numValoraciones,
            'valoracion' => $nueva_valoracion
        )
    );

    $coleccion_valoracion->updateOne($consulta_valoracion, $actualizacion);
}

?>