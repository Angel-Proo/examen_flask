# %% [markdown]
# # Examen de Python
# ### Este examen abarca temas basicos de python con Flask, Flask-Jinja, SocketIO y Pyodbc

# %% [markdown]
# ##### Importa las librerias de Python que ocuparas
# * aqui debes incluir importes a tu propio codigo

# %%
from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO
import random
import socket
import pyodbc
import json

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

# %% [markdown]
# ##### Crea las variables para iniciar tu app, asi como la configuracion de tu variable socketio

# %%
password = hex(random.randint(0,10000))

app = Flask(__name__)
app.config['SECRET_KEY'] = password
socketio = SocketIO(app)

# %% [markdown]
# #### Crea la clase para la conexion a la base de datos con Pyodbc, eres libre de crear la estructura

# %%
class ConexionBasedeDatos:
    def __init__(self, servidor,base,usuario,contraseña):
        self.servidor = servidor
        self.base = base
        self.usuario = usuario
        self.contraseña = contraseña
        self.conexion = None
        
    def conectar(self):
        try:
            strconexion = f"DRIVER={{ODBC Driver 17 for SQL Server}}; SERVER={self.servidor};DATABASE={self.base};UID={self.usuario};PWD={self.contraseña}"
            self.conexion = pyodbc.connect(strconexion)
            print('Conexion exitosa'.center(50,'*'))
            
        except pyodbc.Error as error:
            print(f'Error de conexion: {str(error)}')
            
    def cerrar_conexion(self):
        if self.conexion is not None:
            self.conexion.close()
            print('Conexion cerrada'.center(50,'*'))
            
    def ejecutar_query(self,query):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(query)
            filas = cursor.fetchall()
            return filas
        
        except pyodbc.Error as error:
            print(f'Error en consulta: {str(error)}')
            
    def ejecutar_query_one(self,query):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(query)
            filas = cursor.fetchone()
            return filas
        
        except pyodbc.Error as error:
            print(f'Error en consulta: {str(error)}')
 
    def ejecutar_instruccion(self,query):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(query)
            cursor.commit()
            return 'Se ejecuto correctamente'.center(50,'*')
        except pyodbc.Error as error:
            print(f'Error en consulta: {str(error)}')
            
conexion = ConexionBasedeDatos('SP-DR','s4','s4_admin','admin')

# %% [markdown]
# #### Crea una clase FormUsuario con wtforms, crea un formulario con wtforms con los siguientes campos y documentalo
# * Usuario
# * Contraseña
# * Area "Debe ser una consulta SQL"
# * Sub Area "Debe depender del valor del area"
# ### Si no usar wtfors, hazlo directo en HTML pero debes implementar SocketIO en ambos casos para llenar el campo de puesto en funcion de la seleccion del Area

# %%
class FormUsuario(FlaskForm):
    usuario = StringField('Usuario')
    contraseña = StringField('Contraseña')
    area = SelectField('Selecciona Area')
    puesto = SelectField('Seleccionar Puesto')
    boton = SubmitField('Enviar')

    def __init__(self,*args,**kargs):
        super(FormUsuario, self).__init__(*args,**kargs)
        self.area.choices = self.buscar_opciones()
        
    def buscar_opciones(self):
        conexion.conectar() 
        consulta = "SELECT id_area, area_descripcion FROM Tabla_Areas WHERE area_activo = 1"
        resultado = conexion.ejecutar_query(consulta)
        opciones = [(dato[0], dato[1]) for dato in resultado]
        opciones.insert(0,('',f'Selecciona Area'))
        conexion.cerrar_conexion()
        return opciones   

# %% [markdown]
# #### Crea tu ruta principal que cumpla estos requisitos
# * La ruta debe generarse en / y /home
# * Agregar el metodo es opcional
# * Se debe renderizar el html con el nombre 'index.html'
# * Envia por variable tu nombre completo y crea un boton que te envie con url_for a la ruta '/formulario'

# %%
@app.route('/')
@app.route('/home')
def index():
    nombre = 'Angel de Jesus Proo Martinez'
    return render_template('index.html', nombre = nombre)

# %% [markdown]
# #### Crea la ruta del formulario, renderiza un archivo llamado 'form.html', agrega los metodos get y post
# #### Crea la logica para guardar al nuevo usuario con pyodbc y redireccionar a la funcion 'index'

# %%
@app.route('/formulario', methods=['GET','POST'])
def formulario():
    form = FormUsuario()
    
    if request.method == 'POST':
        conexion.conectar()
        instruccion = f"""INSERT INTO Tabla_Usuarios (usuario, contraseña, id_area, id_puesto) 
                            VALUES('{form.usuario.data}','{form.contraseña.data}',{form.area.data}, {form.puesto.data})"""
        conexion.ejecutar_instruccion(instruccion)
        conexion.cerrar_conexion()
        return redirect(url_for('index'))
    
    return render_template('form.html', form = form)

# %% [markdown]
# #### Aqui ingresa la logica de un socket para recibir el area y otro para mandar la lista de sub areas

# %%
@socketio.on('solicitar_puestos')
def solicitar_puestos(area):
    conexion.conectar()
    consulta = f'SELECT id_puesto, descripcion_puesto FROM Tabla_Puestos WHERE id_area = {area}'
    resultado = conexion.ejecutar_query(consulta)
    print(resultado)
    if len(resultado) == 0 :
        puestos = []
        diccionario = {}
        diccionario['id'] = '0'
        diccionario['puesto'] = 'Sin Puesto'
        puestos.append(diccionario)

    else:
        puestos = []
        for puesto in resultado:
            diccionario = {}
            diccionario['id'] = puesto[0]
            diccionario['puesto'] = puesto[1]
            puestos.append(diccionario)
    
    socketio.emit('puestos',puestos)
            

# %% [markdown]
# #### Ejecuta tu aplicacion flask a traves de un if, levanta la aplicacion con la ip del equipo y el puerto 5000, agrega todas las librerias en un archivo requerimientos.txt y coloca como comentarios el metodo que utilizaste para crearla, asi de como lo instalarias en tu entorno virtual

# %%
if __name__ == '__main__':
    nombre_host = socket.gethostname()
    direccion_ip = socket.gethostbyname(nombre_host)
    #socketio.run(app=app,host=direccion_ip, port=5000)
    app.run(host=direccion_ip, port=5000)
    
    #pip freeze > requerimientos.txt
    #pip install -r requerimientos.txt
    

# %% [markdown]
# #### Genera la lista de todos los usarios que estan en la tabla 'examen_usuarios' y con un boton en un archivo Excel descargala, agrega tu nombre completo al archivo


