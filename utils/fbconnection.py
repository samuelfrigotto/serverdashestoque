from firebird.driver import driver_config
import firebird.driver as fdb
import pandas as pd
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pandas')

curso=None
conn=None
connSql = None

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS 
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

dll_path = os.path.join(base_path, "utils", "dlls", "fb40.dll")

def openConn(dbpath:str):
    global conn
    global curso
    global connSql
    if conn is None:
        fdb.load_api(dll_path)
        driver_config.server_defaults.host.value = "localhost"
        driver_config.server_defaults.user.value = "SYSDBA"
        driver_config.server_defaults.password.value = "masterkey"
        driver_config.server_defaults.port.value = "3060"
        conn = fdb.connect(dbpath)
        curso = conn.cursor()

def closeConn():
    global conn
    global curso
    if conn:
        conn.close()
        conn=None
        curso.close()
        curso=None

def selectAll(tabela, colunas, dbpath):
    global curso
    openConn(dbpath)
    df=None
    try:
        query = f"SELECT {colunas} FROM {tabela}"
        df = pd.read_sql(query, conn)           
    finally:
        closeConn()
    return df

def selectAllDir(tabela, colunas):
    global curso
    global conn
    global connSql
    
    df = pd.DataFrame()
    try:
        openConn()
        query = f"""
        SELECT {colunas} FROM {tabela}
        """
        df = pd.read_sql(query, conn)
    except Exception as e:
        print(e)
    finally:
        closeConn()        
    return df

def selectWhere(tabela, colunas, where):
    global curso
    openConn()   
    try:
        query = f"SELECT {colunas} FROM {tabela} WHERE({where})"
        curso.execute(query)
        columns = [column[0] for column in curso.description]
        rows = curso.fetchall()
        df=pd.DataFrame.from_records(rows,columns=columns)    
    finally:
        closeConn()
    return df

def countRows(tabela):
    global curso
    openConn()
    result=None
    try:
        query= f"SELECT COUNT(*) AS TOTAL_LINHAS FROM {tabela}"
        curso.execute(query)
        result= curso.fetchone()
    finally:
        closeConn()
        return result[0]