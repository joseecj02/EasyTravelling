<?php

require_once 'Conexion.php';

header('Content-Type: application/json');

$datos = json_decode(file_get_contents('php://input'), true);

$id_hotel = $datos['id_hotel'];

if(isset($datos['id_usuario'])){
    $id_usuario = $datos['id_usuario'];
}else{
    $id_usuario = null;
}

if(!$id_hotel){
    echo json_encode(['Error' => 'Faltan parámetros en la solicitud']);
    exit;
}

$id_hotel = (int) $id_hotel;
if(!is_null($id_usuario)){
    $id_usuario = (int) $id_usuario;
}

$conexion = new Conexion();
$db = $conexion->conectar();

$coleccion = $db->comentarios;

$consulta = array(
    'id_hotel' => $id_hotel
);


$comentarios = $coleccion->find($consulta);

$resultados = [];

foreach($comentarios as $comentario){
    $resultados[] = [
        'id' => $comentario['_id'],
        'id_hotel' => $comentario['id_hotel'],
        'id_usuario' => $comentario['id_usuario'],
        'nombreUs' => $comentario['nombreUs'],
        'comentario' => $comentario['comentario'],
        'valoracion' => $comentario['valoracion'],
        'fechaPubli' => $comentario['fechaPubli']
    ];
}

usort($resultados, function($a, $b) use ($id_usuario) {
    if (!is_null($id_usuario)) {
        if ($a['id_usuario'] == $id_usuario && $b['id_usuario'] != $id_usuario) {
            return -1;
        } elseif ($a['id_usuario'] != $id_usuario && $b['id_usuario'] == $id_usuario) {
            return 1;
        }
    }
    return $b['fechaPubli'] <=> $a['fechaPubli'];
});

echo json_encode($resultados);
exit;
?>