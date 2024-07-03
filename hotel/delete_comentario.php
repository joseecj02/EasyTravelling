<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$id_hotel = $datos['id_hotel'];
$id_usuario = $datos['id_usuario'];
$valoracion = $datos['valoracion'];

if(!$id_hotel || !$id_usuario || !$valoracion){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$id_hotel = (int) $id_hotel;
$id_usuario = (int) $id_usuario;
$valoracion = (int) $valoracion;

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->comentarios;
$coleccion_hotel = $db->hotel;

$consulta = array(
    'id_hotel' => $id_hotel,
    'id_usuario' => $id_usuario
);

$comentario = $coleccion->findOne($consulta);

if($comentario){
    $resultado = $coleccion->deleteOne($consulta);
    $consulta_hotel = array(
        '_id' => $id_hotel
    );
    $hotel = $coleccion_hotel->findOne($consulta_hotel);
    #echo json_encode($hotel);
    if($hotel){
        $nueva_ValoracionesTotal = $hotel['ValoracionesTotal'] - $valoracion;
        $nuevo_numValoraciones = $hotel['numValoraciones'] - 1;

        if($nuevo_numValoraciones > 0){
            $nueva_valoracion = round($nueva_ValoracionesTotal / $nuevo_numValoraciones, 1);
        }else{
            $nueva_valoracion = 0;
        }

        $actualizacion = [
            '$set' => [
                'ValoracionesTotal' => $nueva_ValoracionesTotal,
                'numValoraciones' => $nuevo_numValoraciones,
                'valoracion' => $nueva_valoracion
            ]
        ];

        $coleccion_hotel->updateOne($consulta_hotel, $actualizacion);
    }
}

    
echo json_encode(['Mensaje' => 'Comentario eliminado correctamente']);

?>