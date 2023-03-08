import psycopg2
import psycopg2.extras
import os
from PIL import Image

hostname = 'localhost'
database = 'Car_detection'
username = 'postgres'
pwd = 'Glace82649'
port_id = 5432
conn = None

name = 'new.PNG'
num = '1'

empty = 'false'
total = '100'
free = '68'
full ='32'

file_name = Image.open(name)
os.chdir('C:/Users/Owner/Desktop/automne 2022/capstone/version 2/Symfony/public/assets/uploads')
file_name.save(name)


try:
    conn = psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id) 
    
    cur=conn.cursor()    
    
    cur.execute('SELECT * FROM image')
    print(cur.fetchall())
    
    #update image 
    #update_script = 'UPDATE image SET name = %s WHERE id =%s '
    #value = (dekhla,num)
    #cur.execute(update_script,value)
    #update place information
    update_script = 'UPDATE place SET is_empty = %s,total_place=%s,availabl_spot=%s,full_spot=%s,name=%s  WHERE id =%s '
    value = (empty,total,free,full,name,num)
    cur.execute(update_script,value)
    
    conn.commit()

              
except Exception as error:
    print(error)
finally:
    if conn is not None:
        conn.close()