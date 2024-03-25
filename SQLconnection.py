import pyodbc
sqlDbconn = pyodbc.connect(
    "DRIVER={SQL Server Native Client 11.0};"
    "SERVER=DESKTOP-58LJL7D\SQLEXPRESS;"
    "DATABASE=app_db;"
    "Trusted_Connection=no;"
    "UID=Admin;"
    "PWD=Password#1234"
)

def getData(sqlDbconn):
    print("Read")
    cursor = sqlDbconn.cursor();
    cursor.execute("select * from app_db.dbo.docs")
    for row in cursor:
        print(f'{row}')

getData(sqlDbconn)        