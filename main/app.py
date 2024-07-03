from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_mysqldb import  MySQL
from flask_bcrypt import Bcrypt
from flask_session import Session
import json
import requests
import redis
from datetime import datetime
import stripe

def crear_producto(nombre):
    producto = stripe.Product.create(name=nombre)
    return producto.id

stripe.api_key = 'sk_test_51PVwfqIR4tA30KI0IZLzXokOoYFHmcOCQoAP30nPHgr2ZamgPNdvTNQLiIrNj9czRq1LtZR7VSgEnXlOo7c4fJz400HLU1Yytw'

producto_reserva_hotel = crear_producto('Reserva de hotel')
producto_reserva_vuelo = crear_producto('Reserva de vuelo')
producto_reserva_bus = crear_producto('Reserva de bus')

app = Flask(__name__)

#Configuración de la sesión
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_REDIS'] = redis.StrictRedis(host='redis', port=6379)
Session(app)

#Conexion MySQL
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tfg_viajes'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_PORT'] = 3306
mysql = MySQL(app)
bcrypt = Bcrypt(app)

@app.route('/')
def go_main_page():
    return redirect(url_for('main_page'))

@app.route('/main_page', methods=['POST', 'GET'])
def main_page():
    usuario = None
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()
    
    hotel_buscado = 'False'
    
    response = requests.post('http://tfg-hotel-web-1:5005/hotel_valoracion.php')

    resultados = response.json()

    if resultados:
        if usuario:
            return render_template('main_page.html', resultados = resultados, hotel_buscado = hotel_buscado, usuario = usuario)
        else:
            return render_template('main_page.html', resultados = resultados, hotel_buscado = hotel_buscado)

@app.route('/buscar_bus', methods=['POST', 'GET'])
def buscar_bus():
    usuario = None
    
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()

    if request.method == 'POST':
        origen = request.form['origen']
        destino = request.form['destino']
        fecha = request.form['fecha']
        filtro = request.form['filtro']

        origen_transformado = origen.replace('Ñ', 'N').replace('ñ','n')
        destino_transformado = destino.replace('Ñ', 'N').replace('ñ','n')

        consulta = {'origen': origen_transformado, 'destino': destino_transformado, 'fecha': fecha, 'filtro': filtro}

        response = requests.get(f'http://tfg-bus-web-1:5003/servicio_bus.php', json = consulta)

        resultados = response.json()
        
        if resultados:
            if usuario:
                return render_template('buscar_bus.html', resultados = resultados, usuario = usuario)
            else:
                return render_template('buscar_bus.html', resultados = resultados)
        else:
            if usuario:
                return render_template('buscar_bus.html', mensaje='No se encontraron resultados coincidentes.', usuario = usuario)
            else:
                return render_template('buscar_bus.html', mensaje='No se encontraron resultados coincidentes.')

    if usuario:    
        return render_template('buscar_bus.html', usuario = usuario)
    else:
        return render_template('buscar_bus.html')

@app.route('/buscar_vuelo', methods=['POST', 'GET'])
def buscar_vuelo():
    usuario = None
    
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()

    if request.method == 'POST':
        origen = request.form['origen']
        destino = request.form['destino']
        fecha = request.form['fecha']
        filtro = request.form['filtro']

        origen_transformado = origen.replace('Ñ', 'N').replace('ñ','n')
        destino_transformado = destino.replace('Ñ', 'N').replace('ñ','n')

        consulta = {'origen': origen_transformado, 'destino': destino_transformado, 'fecha': fecha, 'filtro': filtro}

        response = requests.get(f'http://tfg-flight-web-1:5004/servicio_flight.php', json = consulta)

        resultados = response.json()
        
        if resultados:
            if usuario:
                return render_template('buscar_vuelo.html', resultados = resultados, usuario = usuario)
            else:
                return render_template('buscar_vuelo.html', resultados = resultados)
        else:
            if usuario:
                return render_template('buscar_vuelo.html', mensaje='No se encontraron resultados coincidentes.', usuario = usuario)
            else:
                return render_template('buscar_vuelo.html', mensaje='No se encontraron resultados coincidentes.')
    

    if usuario:    
        return render_template('buscar_vuelo.html', usuario = usuario)
    else:
        return render_template('buscar_vuelo.html')
    
@app.route('/buscar_hotel', methods=['POST', 'GET'])
def buscar_hotel():
    usuario = None
    hotel_buscado = 'True'

    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()

    if request.method == 'POST':
        ubicacion = request.form.get('ubicacion', '')
        filtro = request.form.get('filtro', '')
        fecha_llegada = request.form.get('fecha_llegada', '')
        fecha_salida = request.form.get('fecha_salida', '')

        ubicacion_transformada = ubicacion.replace('Ñ', 'N').replace('ñ','n')
        consulta = {'ubicacion': ubicacion_transformada, 'filtro': filtro}

        response = requests.get(f'http://tfg-hotel-web-1:5005/servicio_hotel.php', json = consulta)

        resultados = response.json()
        
        if resultados:
            if usuario:
                return render_template('buscar_hotel.html', fecha_salida = fecha_salida, fecha_llegada = fecha_llegada, resultados = resultados, usuario = usuario, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado)
            else:
                return render_template('buscar_hotel.html', fecha_salida = fecha_salida, fecha_llegada = fecha_llegada, resultados = resultados, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado)
        else:
            if usuario:
                return render_template('buscar_hotel.html', mensaje='No se encontraron resultados coincidentes.', fecha_salida = fecha_salida, fecha_llegada = fecha_llegada, usuario = usuario, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado)
            else:
                return render_template('buscar_hotel.html', mensaje='No se encontraron resultados coincidentes.', fecha_salida = fecha_salida, fecha_llegada = fecha_llegada, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado)

    if usuario:    
        return render_template('buscar_hotel.html', usuario = usuario)
    else:
        return render_template('buscar_hotel.html')
    
@app.route('/comentarios_<string:nombre>', methods=['POST', 'GET'])
def comentarios_hotel(nombre):
    usuario = None
    usuario_encontrado = False
    filtro = request.form.get('filtro', '')
    ubicacion = request.form.get('ubicacion', '')
    fecha_llegada = request.form.get('fecha_llegada', '')
    fecha_salida = request.form.get('fecha_salida', '')

    hotel_buscado = request.form.get('hotel_buscado', request.args.get('hotel_buscado', ''))

    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()

    if 'id' in request.form and request.form['id']:
        id_hotel = request.form['id']
    else:
        response = requests.get(f'http://tfg-hotel-web-1:5005/id_hotel.php', json = {'nombre': nombre})
        id_recibido = response.json()
        id_hotel_string = id_recibido[0]['id']
        id_hotel = int(id_hotel_string)

    if usuario: 
        consulta = {'id_hotel': id_hotel, 'id_usuario': id}

        response = requests.get(f'http://tfg-hotel-web-1:5005/comentarios.php', json = consulta)

    else:   
        consulta = {'id_hotel': id_hotel}

        response = requests.get(f'http://tfg-hotel-web-1:5005/comentarios.php', json = consulta)

    resultados = response.json()

    for resultado in resultados:
        id_usuario_comentarios = resultado['id_usuario']
        if id_usuario_comentarios == id:
            usuario_encontrado = True
            break

    if usuario_encontrado != True:
        id = 0

    if resultados:
        if usuario:
            return render_template('comentarios_hotel.html', fecha_salida = fecha_salida, fecha_llegada = fecha_llegada, usuario = usuario, resultados = resultados, id_usuario = id, nombre = nombre, id_hotel = id_hotel, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado)
        else:
            return render_template('comentarios_hotel.html', id_usuario=id, fecha_salida = fecha_salida, fecha_llegada = fecha_llegada, resultados = resultados, nombre = nombre, id_hotel = id_hotel, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado)
    else:
        if usuario:
            return render_template('comentarios_hotel.html', mensaje='No se encontraron comentarios.', fecha_salida = fecha_salida, fecha_llegada = fecha_llegada, usuario = usuario, id_usuario = id, nombre = nombre, id_hotel = id_hotel, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado)    
        else:
            return render_template('comentarios_hotel.html', mensaje='No se encontraron comentarios.', id_usuario=id, fecha_salida = fecha_salida, fecha_llegada = fecha_llegada, nombre = nombre, id_hotel = id_hotel, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado)
    
@app.route('/add_comentario_<string:nombre>', methods=['POST', 'GET'])
def add_comentario_hotel(nombre):
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT nombreUs FROM usuario WHERE id = %s", (id,))
        nombreUs = cur.fetchone()['nombreUs']
        cur.close()

        hotel_buscado = request.form.get('hotel_buscado', request.args.get('hotel_buscado', ''))

        if 'id' in request.form and request.form['id']:
            id_hotel = request.form['id']
        else:
            response = requests.get(f'http://tfg-hotel-web-1:5005/id_hotel.php', json = {'nombre': nombre})
            id_recibido = response.json()
            id_hotel_string = id_recibido[0]['id']
            id_hotel = int(id_hotel_string)

        ubicacion = request.form.get('ubicacion', request.args.get('ubicacion', ''))
        filtro = request.form.get('filtro', request.args.get('filtro', ''))
        fecha_llegada = request.form.get('fecha_llegada', request.args.get('fecha_llegada',''))
        fecha_salida = request.form.get('fecha_salida', request.args.get('fecha_salida',''))

        id_usuario = session['user_id']
        fecha = datetime.now() 
        fechaPubli = fecha.strftime('%Y-%m-%d')
        comentario = request.form['comentario']
        valoracion = request.form['valoracion']

        consulta = {'id_hotel': id_hotel, 'id_usuario': id_usuario, 'nombreUs': nombreUs, 'comentario': comentario, 'valoracion': valoracion, 'fechaPubli': fechaPubli}

        requests.post(f'http://tfg-hotel-web-1:5005/add_comentario.php', json = consulta)

        return redirect(url_for('comentarios_hotel', nombre = nombre, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado, fecha_salida = fecha_salida, fecha_llegada = fecha_llegada))

    else:
        return redirect(f"http://127.0.0.1:5002/go_login")
    
@app.route('/delete_comentario_<string:nombre>_<string:id_usuario>_<string:id_hotel>', methods=['POST', 'GET']) 
def delete_comentario_hotel(nombre, id_usuario, id_hotel):
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()

        hotel_buscado = request.form.get('hotel_buscado', request.args.get('hotel_buscado', ''))

        valoracion = request.form['valoracion']
        ubicacion = request.form.get('ubicacion', request.args.get('ubicacion', ''))
        filtro = request.form.get('filtro', request.args.get('filtro', ''))
        fecha_llegada = request.form.get('fecha_llegada', request.args.get('fecha_llegada',''))
        fecha_salida = request.form.get('fecha_salida', request.args.get('fecha_salida',''))

        consulta_delete = {'id_usuario': id_usuario, 'id_hotel': id_hotel, 'valoracion': valoracion}

        requests.post(f'http://tfg-hotel-web-1:5005/delete_comentario.php', json = consulta_delete)

        return redirect(url_for('comentarios_hotel', nombre = nombre, ubicacion = ubicacion, filtro = filtro, hotel_buscado = hotel_buscado, fecha_salida = fecha_salida, fecha_llegada = fecha_llegada)) 
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")

@app.route('/reservar_bus', methods=['POST', 'GET'])
def reservar_bus():
    if(session.get('logged') == True):
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()

        id_bus = request.form['id']
        precio = request.form['precio']
        nombre_empresa = request.form['nombre_empresa']
        hora_salida = request.form['hora_salida']
        hora_llegada = request.form['hora_llegada']
        origen = request.form['origen']
        destino = request.form['destino']
        fecha = request.form['fecha']
        filtro = request.form['filtro']
        tipo_reserva = "Bus"
        estado = "Reservado"

        return render_template('reservar_bus.html', estado = estado, filtro = filtro, hora_salida = hora_salida, hora_llegada = hora_llegada, tipo_reserva = tipo_reserva, id_bus = id_bus, precio = precio, nombre_empresa = nombre_empresa, destino = destino, origen = origen, fecha = fecha, usuario = usuario)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")

@app.route('/confirmar_reserva_bus', methods=['POST', 'GET'])
def confirmar_reserva_bus():
    if(session.get('logged') == True):
        id = session['user_id']

        reserva_bus = session['reserva_bus']

        id_bus = reserva_bus['id_bus']
        precio = reserva_bus['precio']
        nombre_empresa = reserva_bus['nombre_empresa']
        hora_salida = reserva_bus['hora_salida']
        hora_llegada = reserva_bus['hora_llegada']
        origen = reserva_bus['origen']
        destino = reserva_bus['destino']
        fecha = reserva_bus['fecha']
        filtro = reserva_bus['filtro']
        tipo_reserva = reserva_bus['tipo_reserva']
        estado = reserva_bus['estado']

        consulta = {'estado': estado, 'id_bus': id_bus, 'id_usuario': id, 'precio': precio, 'nombre_empresa': nombre_empresa, 'origen': origen, 'destino': destino, 'fecha': fecha, 'hora_salida': hora_salida, 'hora_llegada': hora_llegada, 'tipo_reserva': tipo_reserva}


        response = requests.post(f'http://tfg-reserves-payment-web-1:5006/add_reserva_bus.php', json = consulta)

        
        return render_template('confirmacion_bus.html', origen=origen, destino=destino, fecha=fecha, filtro=filtro)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")
    
@app.route('/reservar_vuelo', methods=['POST', 'GET'])
def reservar_vuelo():
    if(session.get('logged') == True):
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()

        id_vuelo = request.form['id']
        precio = request.form['precio']
        nombre_empresa = request.form['nombre_empresa']
        hora_salida = request.form['hora_salida']
        hora_llegada = request.form['hora_llegada']
        origen = request.form['origen']
        destino = request.form['destino']
        fecha = request.form['fecha']
        filtro = request.form['filtro']
        tipo_reserva = "Vuelo"
        estado = "Reservado"

        return render_template('reservar_vuelo.html', estado = estado, usuario = usuario, filtro = filtro, hora_salida = hora_salida, hora_llegada = hora_llegada, tipo_reserva = tipo_reserva, id_vuelo = id_vuelo, precio = precio, nombre_empresa = nombre_empresa, destino = destino, origen = origen, fecha = fecha)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")
    
@app.route('/confirmar_reserva_vuelo', methods=['POST', 'GET'])
def confirmar_reserva_vuelo():
    if(session.get('logged') == True):
        id = session['user_id']

        reserva_vuelo = session['reserva_vuelo']

        id_vuelo = reserva_vuelo['id_vuelo']
        precio = reserva_vuelo['precio']
        nombre_empresa = reserva_vuelo['nombre_empresa']
        hora_salida = reserva_vuelo['hora_salida']
        hora_llegada = reserva_vuelo['hora_llegada']
        origen = reserva_vuelo['origen']
        destino = reserva_vuelo['destino']
        fecha = reserva_vuelo['fecha']
        filtro = reserva_vuelo['filtro']
        tipo_reserva = reserva_vuelo['tipo_reserva']
        estado = reserva_vuelo['estado']

        consulta = {'estado': estado, 'id_vuelo': id_vuelo, 'id_usuario': id, 'precio': precio, 'nombre_empresa': nombre_empresa, 'origen': origen, 'destino': destino, 'fecha': fecha, 'hora_salida': hora_salida, 'hora_llegada': hora_llegada, 'tipo_reserva': tipo_reserva}

        requests.post(f'http://tfg-reserves-payment-web-1:5006/add_reserva_vuelo.php', json = consulta)
        
        return render_template('confirmacion_vuelo.html', origen=origen, destino=destino, fecha=fecha, filtro=filtro)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")

@app.route('/reservar_hotel', methods=['POST', 'GET'])
def reservar_hotel():
    if(session.get('logged') == True):
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.close()

        id_hotel = request.form['id']
        fecha_salida = request.form['fecha_salida']
        fecha_llegada = request.form['fecha_llegada']
        ubicacion = request.form['ubicacion']
        filtro = request.form['filtro']
        precio = request.form['precio']
        nombre = request.form['nombre']
        estrellas = request.form['estrellas']
        direccion = request.form['direccion']
        imagen = request.form['imagen']
        tipo_reserva = "Hotel"
        estado = "Reservado" 
        hotel_buscado = request.form.get('hotel_buscado', '')

        if(fecha_llegada and fecha_salida):
            fecha_llegada_dt = datetime.strptime(fecha_llegada, '%Y-%m-%d')
            fecha_salida_dt = datetime.strptime(fecha_salida, '%Y-%m-%d')
            dias = (fecha_salida_dt - fecha_llegada_dt).days
            precio_total = dias * int(precio)
        else:
            precio_total = precio

        return render_template('reservar_hotel.html', imagen = imagen, hotel_buscado = hotel_buscado, estado = estado, nombre = nombre, estrellas = estrellas, direccion = direccion, tipo_reserva = tipo_reserva, id_hotel = id_hotel, fecha_llegada = fecha_llegada, fecha_salida = fecha_salida, ubicacion = ubicacion, filtro = filtro, precio = precio_total, usuario = usuario)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")

@app.route('/confirmar_reserva_hotel', methods=['POST', 'GET'])
def confirmar_reserva_hotel():
    if(session.get('logged') == True):
        reserva_hotel = session['reserva_hotel']

        id = session['user_id']
        id_hotel = reserva_hotel['id_hotel']
        fecha_salida = reserva_hotel['fecha_salida_hidden']
        fecha_llegada = reserva_hotel['fecha_llegada_hidden']
        ubicacion = reserva_hotel['ubicacion']
        filtro = reserva_hotel['filtro']
        precio = reserva_hotel['precio_hidden']
        nombre = reserva_hotel['nombre']
        estrellas = reserva_hotel['estrellas']
        direccion = reserva_hotel['direccion']
        tipo_reserva = reserva_hotel['tipo_reserva']
        estado = reserva_hotel['estado']
        hotel_buscado = reserva_hotel['hotel_buscado']
        imagen = reserva_hotel['imagen']

        consulta = {'imagen': imagen, 'estado': estado, 'id_hotel': id_hotel, 'id_usuario': id, 'precio': precio, 'nombre': nombre, 'estrellas': estrellas, 
                    'direccion': direccion, 'ubicacion': ubicacion, 'fecha_llegada': fecha_llegada, 'fecha_salida': fecha_salida, 'tipo_reserva': tipo_reserva}

        requests.post(f'http://tfg-reserves-payment-web-1:5006/add_reserva_hotel.php', json = consulta)
        
        return render_template('confirmacion_hotel.html', ubicacion=ubicacion, fecha_llegada=fecha_llegada, fecha_salida=fecha_salida, filtro=filtro, hotel_buscado = hotel_buscado)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")

@app.route('/mis_reservas', methods=['POST', 'GET'])
def mis_reservas():
    if(session.get('logged') == True):
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()
        cur.execute("SELECT nombreUs FROM usuario WHERE id = %s", (id,))
        nombreUs = cur.fetchone()['nombreUs']
        cur.close()

        if request.form:
            tipo_reserva = request.form['tipo_reserva']
            if(tipo_reserva == 'Hotel'):
                estado = request.form['estado']
                id_reserva = request.form['id_reserva']

                requests.post(f'http://tfg-reserves-payment-web-1:5006/update_estado_reserva.php', json = {'estado': estado, 'id_reserva': id_reserva})

            elif(tipo_reserva == 'Vuelo'):
                estado = request.form['estado']
                id_reserva = request.form['id_reserva']

                requests.post(f'http://tfg-reserves-payment-web-1:5006/update_estado_reserva.php', json = {'estado': estado, 'id_reserva': id_reserva})
            else:
                estado = request.form['estado']
                id_reserva = request.form['id_reserva']

                requests.post(f'http://tfg-reserves-payment-web-1:5006/update_estado_reserva.php', json = {'estado': estado, 'id_reserva': id_reserva})

    

        response = requests.post(f'http://tfg-reserves-payment-web-1:5006/mis_reservas.php', json = {'id_usuario': id})

        resultados = response.json()

        if resultados:
            return render_template('mis_reservas.html', usuario = usuario, resultados = resultados, nombreUs = nombreUs)
        else:
            return render_template('mis_reservas.html', usuario = usuario, nombreUs = nombreUs, mensaje='No has hecho ninguna reserva.')
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")


@app.route('/sesion_pago_hotel', methods=['POST', 'GET'])
def sesion_pago_hotel():
    if request.method == 'POST':
        precio = float(request.form['precio_hidden'])

        session['reserva_hotel'] = {
            'id_hotel': request.form['id_hotel'],
            'fecha_salida_hidden': request.form['fecha_salida_hidden'],
            'fecha_llegada_hidden': request.form['fecha_llegada_hidden'],
            'ubicacion': request.form['ubicacion'],
            'filtro': request.form['filtro'],
            'precio_hidden': request.form['precio_hidden'],
            'nombre': request.form['nombre'],
            'estrellas': request.form['estrellas'],
            'direccion': request.form['direccion'],
            'tipo_reserva': request.form['tipo_reserva'],
            'estado': request.form['estado'],
            'hotel_buscado': request.form['hotel_buscado'],
            'imagen': request.form['imagen']
        }
        try:
            precios_existentes = stripe.Price.list()

            precio_existente = None

            for p in precios_existentes['data']:
                if p['unit_amount'] == int(precio*100):
                    precio_existente = p['id']
                    break
            
            if not precio_existente:
                nuevo_precio = stripe.Price.create(
                    unit_amount = int(precio*100),
                    currency = 'eur',
                    product = producto_reserva_hotel,
                )
                precio_existente = nuevo_precio['id']
            
            sesion_pago = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': precio_existente,
                        'quantity': 1,
                    },
                ],
                mode = 'payment',
                success_url = url_for('confirmar_reserva_hotel', _external=True),
                cancel_url = url_for('error_reserva_hotel', _external=True),  
            )
        except Exception as e:
            return str(e)
        
    return redirect(sesion_pago.url)

@app.route('/error_reserva_hotel', methods=['POST', 'GET'])
def error_reserva_hotel():
    if(session.get('logged') == True):
        reserva_hotel = session['reserva_hotel']

        fecha_salida = reserva_hotel['fecha_salida_hidden']
        fecha_llegada = reserva_hotel['fecha_llegada_hidden']
        ubicacion = reserva_hotel['ubicacion']
        filtro = reserva_hotel['filtro']
        hotel_buscado = reserva_hotel['hotel_buscado']

        return render_template('error_reserva_hotel.html', ubicacion=ubicacion, fecha_llegada=fecha_llegada, fecha_salida=fecha_salida, filtro=filtro, hotel_buscado = hotel_buscado)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")

@app.route('/sesion_pago_bus', methods=['POST', 'GET'])
def sesion_pago_bus():
    if request.method == 'POST':
        precio = float(request.form['precio'])

        session['reserva_bus'] = {
            'id_bus': request.form['id_bus'],
            'fecha': request.form['fecha'],
            'precio': request.form['precio'],
            'nombre_empresa': request.form['nombre_empresa'],
            'hora_salida': request.form['hora_salida'],
            'hora_llegada': request.form['hora_llegada'],
            'origen': request.form['origen'],
            'destino': request.form['destino'],
            'filtro': request.form['filtro'],
            'tipo_reserva': request.form['tipo_reserva'],
            'estado': request.form['estado']
        }
        try:
            precios_existentes = stripe.Price.list()

            precio_existente = None

            for p in precios_existentes['data']:
                if p['unit_amount'] == int(precio*100):
                    precio_existente = p['id']
                    break
            
            if not precio_existente:
                nuevo_precio = stripe.Price.create(
                    unit_amount = int(precio*100),
                    currency = 'eur',
                    product = producto_reserva_bus,
                )
                precio_existente = nuevo_precio['id']
            
            sesion_pago = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': precio_existente,
                        'quantity': 1,
                    },
                ],
                mode = 'payment',
                success_url = url_for('confirmar_reserva_bus', _external=True),
                cancel_url = url_for('error_reserva_bus', _external=True),  
            )
        except Exception as e:
            return str(e)
        
    return redirect(sesion_pago.url)

@app.route('/error_reserva_bus', methods=['POST', 'GET'])
def error_reserva_bus():
    if(session.get('logged') == True):

        reserva_vuelo = session['reserva_bus']

        origen = reserva_vuelo['origen']
        destino = reserva_vuelo['destino']
        fecha = reserva_vuelo['fecha']
        filtro = reserva_vuelo['filtro']
        
        return render_template('error_reserva_bus.html', origen=origen, destino=destino, fecha=fecha, filtro=filtro)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")

@app.route('/sesion_pago_vuelo', methods=['POST', 'GET'])
def sesion_pago_vuelo():
    if request.method == 'POST':
        precio = float(request.form['precio'])

        session['reserva_vuelo'] = {
            'id_vuelo': request.form['id_vuelo'],
            'fecha': request.form['fecha'],
            'precio': request.form['precio'],
            'nombre_empresa': request.form['nombre_empresa'],
            'hora_salida': request.form['hora_salida'],
            'hora_llegada': request.form['hora_llegada'],
            'origen': request.form['origen'],
            'destino': request.form['destino'],
            'filtro': request.form['filtro'],
            'tipo_reserva': request.form['tipo_reserva'],
            'estado': request.form['estado']
        }
        try:
            precios_existentes = stripe.Price.list()

            precio_existente = None

            for p in precios_existentes['data']:
                if p['unit_amount'] == int(precio*100):
                    precio_existente = p['id']
                    break
            
            if not precio_existente:
                nuevo_precio = stripe.Price.create(
                    unit_amount = int(precio*100),
                    currency = 'eur',
                    product = producto_reserva_vuelo,
                )
                precio_existente = nuevo_precio['id']
            
            sesion_pago = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': precio_existente,
                        'quantity': 1,
                    },
                ],
                mode = 'payment',
                success_url = url_for('confirmar_reserva_vuelo', _external=True),
                cancel_url = url_for('error_reserva_vuelo', _external=True),  
            )
        except Exception as e:
            return str(e)
        
    return redirect(sesion_pago.url)

@app.route('/error_reserva_vuelo', methods=['POST', 'GET'])
def error_reserva_vuelo():
    if(session.get('logged') == True):

        reserva_vuelo = session['reserva_vuelo']

        origen = reserva_vuelo['origen']
        destino = reserva_vuelo['destino']
        fecha = reserva_vuelo['fecha']
        filtro = reserva_vuelo['filtro']
        
        return render_template('error_reserva_vuelo.html', origen=origen, destino=destino, fecha=fecha, filtro=filtro)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")


if __name__ == '__main__':
    app.secret_key='joseecj02'
    app.run(host="0.0.0.0", debug=True, port=5000)
