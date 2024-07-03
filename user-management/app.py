from flask import Flask, request, jsonify, render_template, flash, session, redirect, url_for
from kafka import KafkaProducer
from flask_mysqldb import  MySQL
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt, check_password_hash
from flask_session import Session
from datetime import datetime, timedelta
import json
import redis
import requests

app = Flask (__name__)

#Kafka
gestion_usuarios = KafkaProducer(bootstrap_servers='kafka:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

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

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/create_register', methods = ["GET", "POST"])
def create_register():

    nombre = request.form['nombre']
    apellido1 = request.form['apellido1']
    apellido2 = request.form['apellido2']
    nombreUs = request.form['nombreUs']
    fechaNac = request.form['fechaNac']
    correo = request.form['correo']
    password = request.form['password']

    if len(password) < 8 or len(password) > 30:
        return render_template("register.html", nombre=nombre, apellido1=apellido1, apellido2=apellido2, nombreUs=nombreUs, fechaNac=fechaNac, correo=correo, password=password, mensaje="La contraseña debe de tener entre 8 y 30 caracteres.")
    
    try:
        fecha_nacimiento = datetime.strptime(fechaNac, '%Y-%m-%d')
        hoy = datetime.today()

        if fecha_nacimiento > hoy:
            return render_template("register.html", nombre=nombre, apellido1=apellido1, apellido2=apellido2, nombreUs=nombreUs, fechaNac=fechaNac, correo=correo, password=password, mensaje1="La fecha de nacimiento no puede ser mayor a la fecha actual.")
        
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

        if edad < 18:
            return render_template("register.html", nombre=nombre, apellido1=apellido1, apellido2=apellido2, nombreUs=nombreUs, fechaNac=fechaNac, correo=correo, password=password, mensaje3="Debes de ser mayor de 18 años.")
    except ValueError:
        return render_template("register.html", nombre=nombre, apellido1=apellido1, apellido2=apellido2, nombreUs=nombreUs, fechaNac=fechaNac, correo=correo, password=password, mensaje4="La fecha de nacimiento no es válida.")

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
    correo_existente = cur.fetchone()
    cur.close()

    if correo_existente:
        return render_template("register.html", nombre=nombre, apellido1=apellido1, apellido2=apellido2, nombreUs=nombreUs, fechaNac=fechaNac, correo=correo, password=password, mensaje2="Ya existe una cuenta registrada con este correo.")

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuario (nombre, apellido1, apellido2, nombreUs, fechaNac, correo, password) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nombre, apellido1, apellido2, nombreUs, fechaNac, correo, password_hash))
    mysql.connection.commit()

    cur.execute("SELECT id FROM usuario WHERE correo = %s", (correo,))
    user_id = cur.fetchone()['id']
    cur.close()

    #Enviamos los datos con Kafka
    datos_login = {
        'correo': correo,
        'password': password_hash
    }
    gestion_usuarios.send('usuario', value=datos_login)

    #Iniciar sesión automáticamente
    session['user_id'] = user_id
    session['logged'] = True
    session['user'] = {'correo': correo, 'password': password_hash}

    return redirect(f"http://127.0.0.1:5000/main_page")

@app.route('/go_change_password')
def go_change_password():
    if session.get('logged') != True:
        return redirect(f"http://127.0.0.1:5002/go_login")
    else:
        return redirect(url_for('ask_password'))

@app.route('/ask_password', methods=['POST', 'GET'])
def ask_password():
    
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()

        if request.method == 'POST':
            password = request.form['password']

            if usuario and bcrypt.check_password_hash(usuario['password'], password):
                return redirect(url_for('change_password'))
            else:
                return render_template("ask_password.html", usuario=usuario, mensaje6="Contraseña incorrecta.")
        
        return render_template("ask_password.html", usuario=usuario)
    
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")
    
@app.route('/change_password', methods=['POST', 'GET'])
def change_password():
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()

        if request.method == 'POST':
            password = request.form['password']
            password_confirmacion = request.form['password_confirmacion']

            if password != password_confirmacion:
                return render_template("change_password.html", usuario=usuario, mensaje7="Las contraseñas no coinciden.")
            
            if bcrypt.check_password_hash(usuario['password'], password):
                return render_template("change_password.html", usuario=usuario, mensaje8="La contraseña nueva no puede ser igual a la anterior.")

            if len(password) < 8 or len(password) > 30:
                return render_template("change_password.html", usuario=usuario, mensaje9="La contraseña debe de tener entre 8 y 30 caracteres.")

            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            cur.execute("UPDATE usuario SET password = %s WHERE id = %s", (password_hash, id))
            mysql.connection.commit()
            cur.close()

            return render_template("change_password.html", usuario=usuario, mensaje10="Contraseña modificada con éxito.")

        return render_template("change_password.html", usuario=usuario)
    
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")

@app.route('/edit_account')
def edit_account():
    if session.get('logged') != True:
        return redirect(f"http://127.0.0.1:5002/go_login")
    else:
        return redirect(url_for('edit'))
        


@app.route('/edit', methods = ['GET', 'POST'])
def edit():
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()

        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido1 = request.form['apellido1']
            apellido2 = request.form['apellido2']
            nombreUs = request.form['nombreUs']
            fechaNac = request.form['fechaNac']
            
            try:
                fecha_nacimiento = datetime.strptime(fechaNac, '%Y-%m-%d')
                hoy = datetime.today()

                if fecha_nacimiento > hoy:
                    return render_template("modify_info_acc.html", usuario=usuario, nombre=nombre, apellido1=apellido1, apellido2=apellido2, nombreUs=nombreUs, fechaNac=fechaNac, mensaje1="La fecha de nacimiento no puede ser mayor a la fecha actual.")
                
                edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

                if edad < 18:
                    return render_template("modify_info_acc.html", usuario=usuario, nombre=nombre, apellido1=apellido1, apellido2=apellido2, nombreUs=nombreUs, fechaNac=fechaNac, mensaje2="Debes de ser mayor de 18 años.")
            except ValueError:
                return render_template("modify_info_acc.html", usuario=usuario, nombre=nombre, apellido1=apellido1, apellido2=apellido2, nombreUs=nombreUs, fechaNac=fechaNac, mensaje3="La fecha de nacimiento no es válida.")


            cur.execute("UPDATE usuario SET nombre = %s, apellido1 = %s, apellido2 = %s, nombreUs = %s, fechaNac = %s WHERE id = %s", (nombre, apellido1, apellido2, nombreUs, fechaNac, id))
            mysql.connection.commit()

            consulta = {'nombreUs' : nombreUs, 'id_usuario' : id}

            requests.post('http://tfg-hotel-web-1:5005/edit_nombreUs_comentarios.php', json = consulta)

            return render_template("modify_info_acc.html", usuario=usuario, mensaje4="Información de cuenta modificada con éxito.")
        
        cur.close()
    
        return render_template("modify_info_acc.html", usuario=usuario)
    else:
        return redirect(f"http://127.0.0.1/5002/go_login")
    

@app.route('/delete_account')
def delete_account():
    if session.get('logged') != True:
        return redirect(f"http://127.0.0.1:5002/go_login")
    else:
        return redirect(url_for('delete'))    


@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if session.get('logged') == True:
        id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        usuario = cur.fetchone()

        if request.method == 'POST':
            password = request.form['password']

            if usuario and bcrypt.check_password_hash(usuario['password'], password):

                consulta = {'id_usuario' : id}

                requests.post('http://tfg-hotel-web-1:5005/eliminar_todos_comentarios.php', json = consulta)
                requests.post('http://tfg-reserves-payment-web-1:5006/eliminar_todas_reservas.php', json = consulta)

                cur.execute("DELETE FROM usuario WHERE id = %s", (id,))
                mysql.connection.commit()
                cur.close()
                session.clear()
                return redirect(f"http://127.0.0.1:5000/")
            else:
                return render_template("delete.html", usuario=usuario, mensaje3="Contraseña incorrecta.")

        return render_template("delete.html", usuario=usuario)
    else:
        return redirect(f"http://127.0.0.1:5002/go_login")
    
if __name__ == '__main__':
    app.secret_key='joseecj02'
    app.run(host="0.0.0.0", debug=True, port=5001) 
