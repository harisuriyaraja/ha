from flask import Flask, render_template, request
import sqlite3 as sql
import pandas as pd
application =app = Flask(__name__)
import os
import sqlite3
from math import sin, cos, sqrt, atan2, radians
import matplotlib as mpl
mpl.use('Agg')
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
#conn = sqlite3.connect('database.db')
# print("Opened database successfully")
#conn.execute('drop table earthquake')
#conn.execute('CREATE TABLE Earthquake (time text,latitude real,longitude real,depth real,mag real,magType text,nst real,gap real,dmin real,rms real,net text,id text,updated text,place text,type text,horizontalError real,depthError real,magError real,magNst real,status text,locationSource text,magSource text)')
# print("Table created successfully")
# conn.close()

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/enternew')
def upload_csv():
   return render_template('upload.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   if request.method == 'POST':
       con = sql.connect("database.db")
       csv = request.files['myfile']
       file = pd.read_csv(csv)
       file.to_sql('Earthquake', con, schema=None, if_exists='replace', index=True, index_label=None, chunksize=None, dtype=None)	  
       con.close()
       return render_template("result.html",msg = "Record inserted successfully")

@app.route('/list')
def list():
   con = sql.connect("database.db")
 
   
   cur = con.cursor()
   cur.execute("select * from Earthquake")
   
   rows = cur.fetchall();
   con.close()
   return render_template("list.html",rows = rows)

@app.route('/magnitude')
def magnitude():
   return render_template('Magnitude.html')
   
@app.route('/options' , methods = ['POST', 'GET'])
def options():
   con = sql.connect("database.db")
 
   print (request.form['1'])
   print (request.form['1'])
   print (request.form['1'])
   print(request.form['mag'])
   cur = con.cursor()
   row = []
   rows_2 = []
   if request.form['1']== 'greater':
       cur.execute("select Count(*) from Earthquake where mag > ?",(request.form['mag'],))	   
       rows = cur.fetchall()
       cur.execute("select * from Earthquake where mag > ?",(request.form['mag'],))
       rows_2 = cur.fetchall()
   elif request.form['1']== 'lesser':
       cur.execute("select Count (*) from Earthquake where mag < ?",(request.form['mag'],))
       rows = cur.fetchall()
       cur.execute("select * from Earthquake where mag < ?",(request.form['mag'],))
       rows_2 = cur.fetchall()
   else :
       cur.execute("select Count (*) from Earthquake where mag = ?",(request.form['mag'],))
       rows = cur.fetchall()
       cur.execute("select * from Earthquake where mag = ?",(request.form['mag'],))
       rows_2 = cur.fetchall()
   print(len(rows))
   con.close()
   return render_template("list1.html",rows = [rows,rows_2])

@app.route('/range')
def range():
   return render_template('Range.html')
   
@app.route('/values',methods = ['POST', 'GET'])
def values():
   con = sql.connect("database.db")
   print (request.form['mag1'])
   print (request.form['mag2'])
   cur = con.cursor()
   cur.execute("select * from Earthquake WHERE mag BETWEEN ? and ?" ,(request.form['mag1'],request.form['mag2'] ))
   rows = cur.fetchall()
   con.close()
   return render_template("list2.html",rows = rows)
   

@app.route('/location')
def location():
   return render_template('Location.html')
   
@app.route('/distance',methods = ['POST', 'GET'])
def distance():
   con = sql.connect("database.db")
   print (float(request.form['lat1']))
   print (float(request.form['lon1']))
   print (float(request.form['kms']))
   cur = con.cursor()
   cur.execute("select * from Earthquake ")   
   rows = cur.fetchall();
   #ref:https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
   R = 6373.0
   lat1 = radians(float(request.form['lat1']))
   lon1 = radians(float(request.form['lon1']))
   dist =[]
   for row in rows:
       lat2 = radians(row[2])
       lon2 = radians(row[3])
       dlon = lon2 - lon1
       dlat = lat2 - lat1
       a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
       c = 2 * atan2(sqrt(a), sqrt(1 - a))
       distance =float(R * c)
       if distance <= (float(request.form['kms'])):
           dist.append(row)
   con.close()
   return render_template("list3.html",rows = dist)
   
@app.route('/cluster')
def cluster():
   con = sql.connect("database.db")
   cur = con.cursor()
   cur.execute("select latitude,longitude from Earthquake ")    
   #ref:https://mubaris.com/2017/10/01/kmeans-clustering-in-python/
   X = cur.fetchall()
   X = pd.DataFrame(X)
   kmeans = KMeans(n_clusters=3)
   kmeans = kmeans.fit(X)
   labels = kmeans.predict(X)
   centroids = kmeans.cluster_centers_
   print(centroids)
   #colors = ['r', 'g', 'b', 'y', 'c', 'm']
   fig, ax = plt.subplots()
   #for i in range(k):
        #points = np.array([X[j] for j in range(len(X)) if clusters[j] == i])
   ax.scatter(X.iloc[:, 0], X.iloc[:, 1])
   ax.scatter(centroids[:, 0], centroids[:, 1], marker='*')
   fig.savefig('static/img.png')
   return render_template('list4.html',centroids = centroids)
   
@app.route('/night')
def night():
   con = sql.connect("database.db")
   cur = con.cursor()
   cur.execute("select COUNT(*) from Earthquake where mag > 4  ")
   total = cur.fetchall();
   #cur.execute('select COUNT(*) from Earthquake where mag > 4 and "time" Like "%T20:%" or "time" Like "%T21:%" or "time" Like "%T22:%" or "time" Like "%T23:%" or "time" Like "%T00:%" or "time" Like "%T01:%" or "time" Like "%T02:%" or "time" Like "%T03:%" or "time" Like "%T04:%" or "time" Like "%T05:%" ')
   night = cur.fetchall();
   con.close()
   return render_template("list5.html",rows = [total,night])
   
if __name__ == '__main__':
   app.run(debug = True)
