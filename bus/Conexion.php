<?php

require_once __DIR__ . '/vendor/autoload.php';


class Conexion{
    public function conectar(){
        try{
            $servidor = "mongo";
            $baseDatos = "autobus";
            $puerto = "27017";

            $url = "mongodb://" .
                $servidor . ":" .
                $puerto . "/"; 

            $cliente = new \MongoDB\Client($url);
            return $cliente->selectDatabase($baseDatos);
        }catch(\Throwable $th){
            return $th->getMessage();
        }
    }
}

?>