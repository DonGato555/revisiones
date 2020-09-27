import ftplib
import ssl
import os
import errno

import zipfile
import sqlite3
from sqlite3 import Error

from os import scandir, getcwd
from shutil import rmtree

from colorama import Fore, Back, init
init(autoreset=True)




NOMBRE = 'DISPROVALLES'
PASSWORD = 'DI$PR0V@LL3$@supp0rt#2018'

linea = '-' * 60

class ImplicitFTP_TLS(ftplib.FTP_TLS):
    """FTP_TLS subclass that automatically wraps sockets in SSL to support implicit FTPS."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sock = None

    @property
    def sock(self):
        """Return the socket."""
        return self._sock

    @sock.setter
    def sock(self, value):
        """When modifying the socket, ensure that it is ssl wrapped."""
        if value is not None and not isinstance(value, ssl.SSLSocket):
            value = self.context.wrap_socket(value)
        self._sock = value


def ls(ruta = getcwd()):
    #return [arch.name for arch in scandir(ruta) if arch.is_file()]
    return [arch.name for arch in scandir(ruta) if arch.is_dir()]

def limpiar(ruta = getcwd()):
    return [arch.name for arch in scandir(ruta) if arch.is_dir()]


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
 
    return conn

def set_fecha(conn):
    cursorObj = conn.cursor()
    cursorObj.execute('SELECT * FROM GENERAL')
    rows = cursorObj.fetchall()
    for row in rows:
        print(Fore.GREEN + 'Fecha: ' +row[1])
 
def contar_customer_hoy(con, table):

    cursorObj = con.cursor()

    cursorObj.execute("SELECT COUNT(*) FROM "+table+" WHERE CUSVISITTODAY='1'")

    rows = cursorObj.fetchall()

    for row in rows:
        print("CLIENTES PARA VISITA"+": "+str(row[0]))


def cliente_generico(con, table):

    cursorObj = con.cursor()

    cursorObj.execute("SELECT CUSNAME FROM "+table+" WHERE CUSNAME LIKE'%GENERICO%'")

    rows = cursorObj.fetchall()

    for row in rows:
        print("CLIENTE GENERICO"+": "+str(row[0]))

 
def select_tasks(conn, table):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM "+table)
 
    rows = cur.fetchall()
 
    for row in rows:
        print("REGISTROS EN "+table+": "+str(row[0]))

ftp_client = ImplicitFTP_TLS()
ftp_client.connect(host='prd1.xsalesmobile.net', port=990)
ftp_client.login(user=NOMBRE, passwd=PASSWORD)
ftp_client.prot_p()
ftp_client.cwd('XSales_Replication/Download')
#ftp_client.dir()
dirs = []
N = []
print('Listando Rutas :')
ftp_client.dir(dirs.append)
for filename in dirs:
    x = filename[49:]
    if x != 'Backup':
        N.append(x)
print(N)


for DE in N:
    BUSCAR = str(DE)    
    ftp_client = ImplicitFTP_TLS()
    ftp_client.connect(host='prd1.xsalesmobile.net', port=990)
    ftp_client.login(user=NOMBRE, passwd=PASSWORD)
    ftp_client.prot_p()
    ftp_client.cwd('XSales_Replication/Download/'+BUSCAR)
    dirs = []

    DIR= BUSCAR+"_"
    print(linea)
    print('Directorio Creado Ruta:', DIR)
    try:
        os.mkdir(DIR)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    ftp_client.dir(dirs.append)
    for filename in dirs:
        x = filename[49:]
        fhandle = open(DIR+'/'+x, 'wb')
        ftp_client.retrbinary('RETR ' + x, fhandle.write)
        fhandle.close()
            
    ftp_client.close()

    with zipfile.ZipFile(DIR+"/Main.zip","r") as zip_ref:
        zip_ref.extractall(DIR)

    database = DIR+"/Main.sqlite"
    conn = create_connection(database)
    with conn:
        set_fecha(conn)
        select_tasks(conn, "DISCOUNTDETAIL")
        select_tasks(conn, "DISCOUNTROUTE")
        select_tasks(conn, "PROMOTION")
        select_tasks(conn, "PROMOTIONDETAIL")
        select_tasks(conn, "PROMOTIONDETAILPRODUCT")
        select_tasks(conn, "PROMOTIONROUTE")
        contar_customer_hoy(conn, 'CUSTOMER')
        cliente_generico(conn, 'CUSTOMER')
conn.close()

for f in limpiar():
    rmtree(f)
