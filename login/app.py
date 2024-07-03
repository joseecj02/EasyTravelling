from flask import Flask, request, redirect, render_template, url_for, session, jsonify
from flask_mysqldb import  MySQL
from kafka import KafkaConsumer
from flask_session import Session
from flask_bcrypt import Bcrypt
import threading
import redis

app = Flask (__name__)

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

#Kafka
login = KafkaConsumer('login', bootstrap_servers='kafka:9092', value_deserializer=lambda m: m.decode('utf-8'))

def kafka_login():
    for mensaje in login:
        datos_login = mensaje.value
        correo = datos_login['correo']
        password = datos_login['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
        usuario = cur.fetchone()

        if usuario and bcrypt.check_password_hash(usuario['password'], password):
            with app.app_context():
                session['registrado'] = True
                session['id'] = usuario['id']
                session['logged'] = True
                

hebra = threading.Thread(target=kafka_login)
hebra.start()

@app.route('/go_login')
def go_login():
    return render_template('login.html')

@app.route('/login', methods = ["GET", "POST"])  
def login():

    if request.method == 'POST' and 'correo' in request.form and 'password':
        correo = request.form['correo'] 
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE correo = %s", (correo,))
        usuario = cur.fetchone()

        if usuario and bcrypt.check_password_hash(usuario['password'], password):
            session['registrado'] = True

            cur.execute("SELECT id FROM usuario WHERE correo = %s", (correo,))
            user_id = cur.fetchone()['id']
            cur.close()

            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            session['user_id'] = user_id
            session['logged'] = True
            session['user'] = {'correo': correo, 'password': password_hash}

            return redirect(f"http://127.0.0.1:5000/main_page")

        else:
            return render_template("login.html", mensaje5="Credenciales incorrectas." )



@app.route('/logout')
def logout():
    session.pop('logged', None)
    session.pop('user_id', None)
    return redirect(f"http://127.0.0.1:5000/")
   

if __name__ == '__main__':
    app.secret_key='joseecj02'
    app.run(host="0.0.0.0", debug=True, port=5002)