from crypt import methods
from select import select
from sqlite3 import Cursor
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/addemp/", methods=['GET', 'POST'])
def addEmp():
    return render_template('addEmployee.html')


@app.route("/searchemp/", methods=['GET', 'POST'])
def searchEmp():
    return render_template('searchEmployee.html')

@app.route("/displayemp/", methods=['GET', 'POST'])
def displayEmp():
    select_emp = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(select_emp)
    data = cursor.fetchall()
    cursor.close()
    return render_template('displayEmployee.html', employee=data)


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    position = request.form['position']
    department = request.form['department']
    salary = request.form['salary']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, email, phone,position,department,salary))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('addEmployeeOutput.html', name=emp_name)


@app.route("/searchemp",methods=['POST','GET'])
def SearchEmp():

    emp_id = request.form['emp_id']

    select_emp = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    try:
        get = cursor.execute(select_emp,{'emp_id':int(emp_id)})
        if get != 1:
            return "ID not found in database"
        for result in cursor:
            print(result)
            
    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()

        return render_template("searchOutput.html",result=result)
    

@app.route("/emp",methods=['POST','GET'])
def deleteEmp():

    emp_id = request.form['emp_id']
    select_emp = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    delete_emp = "DELETE FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()
    cursor1 = db_conn.cursor()

    try:
        cursor.execute(select_emp, {'emp_id': int(emp_id)})
        cursor1.execute(delete_emp, {'emp_id': int(emp_id)})
        for result in cursor:
            print(result)
        db_conn.commit()
        emp_name = "" + result[1] + " " + result[2]
    except Exception as e:
        db_conn.rollback()
        return str(e)

    finally:
        cursor.close()
        cursor1.close()

    return render_template("deleteOutput.html",name=emp_name)
  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
