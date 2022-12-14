from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime

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
table = 'employee','leave'


@app.route("/", methods=['GET', 'POST'])
def home():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    select_emp = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(select_emp)
    count = cursor.rowcount
    data = cursor
    cursor.close()

    if count == 0:
        return render_template('index.html', noget=True,numEmployee=count)
    else:
        return render_template('index.html', employee=data,noget=False,numEmployee=count)
    

@app.route("/displayatt/", methods=['GET', 'POST'])
def displayAtt():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    select_emp = "SELECT * FROM attendance"
    cursor = db_conn.cursor()
    cursor.execute(select_emp)
    count = cursor.rowcount
    data = cursor
    
     
    cursor.close()
    if count == 0:
        return render_template('displayAtt.html', noget=True,numEmployee=count)
    else:
        return render_template('displayAtt.html', att=data,noget=False,numEmployee=count)
       


@app.route("/addemp/", methods=['GET', 'POST'])
def addEmp():
    return render_template('addEmployee.html')

@app.route("/about/", methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route("/searchemp/", methods=['GET', 'POST'])
def searchEmp():
    return render_template('searchEmployee.html')

@app.route("/displayleave/", methods=['GET', 'POST'])
def displayEmp():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    select_emp = "SELECT * FROM employee.leave"
    cursor = db_conn.cursor()
    cursor.execute(select_emp)
    data = cursor
    count = cursor.rowcount
    cursor.close()
    
    if count == 0:
        return render_template('displayLeave.html', noget=True)
    else:
        return render_template('displayLeave.html', leave=data,noget=False)


@app.route("/addemp", methods=['POST'])
def AddEmp():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    position = request.form['position']
    department = request.form['department']
    salary = request.form['salary']
    emp_image_file = request.files['emp_image_file']
    checkIn = "0000-00-00 00:00:00"

    select_stmt = "SELECT * FROM employee"
    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return render_template('addEmployee.html', alert=True,fileEmpty=True)
    
    try:
        cursor.execute(select_stmt)
        for result in cursor:
            if(emp_id == result[0]):
                return render_template('addEmployee.html', alert=True,id=True)

        try:

            cursor.execute(insert_sql, (emp_id, first_name, last_name, email, phone,position,department,salary,checkIn))
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
            
            finally:
                cursor.close()
                print("all modification done...")
                return render_template('message.html', name=emp_name,alert=True,add=True)

        except Exception as e:
            return str(e)
            
    except Exception as e:
            return str(e)


@app.route("/searchemp",methods=['POST','GET'])
def SearchEmp():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']

    select_emp = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_emp,{'emp_id':int(emp_id)})
        count = cursor.rowcount
       
        for result in cursor:
            print(result)
            
    except Exception as e:
        return str(e)
        
    finally:
        cursor.close()

    if count == 0:
        return render_template('searchEmployee.html', alert=True,searchFail=True)
    else:
        return render_template("searchOutput.html",result=result)
    

@app.route("/delete",methods=['POST','GET'])
def deleteEmp():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    select_emp = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    delete_emp = "DELETE FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_emp, {'emp_id': int(emp_id)})
        for result in cursor:
            print(result)
        emp_name = "" + result[1] + " " + result[2]
    
        
        try:
            cursor.execute(delete_emp, {'emp_id': int(emp_id)})
            db_conn.commit()
        
        finally:
            cursor.close()
            return render_template("message.html",name=emp_name,alert=True,delete=True)

    except Exception as e:
        return str(e)

    
@app.route("/edit",methods=['POST','GET'])
def editEmp():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    select_emp = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    key = "emp-id-" + str(emp_id) + "_image_file"

    url = "https://%s.s3.amazonaws.com/%s" % (custombucket, key)
    try:
        cursor.execute(select_emp, {'emp_id': int(emp_id)})
        for result in cursor:
            print(result)
        db_conn.commit()
        
    except Exception as e:
            db_conn.rollback()
            return str(e)

    finally:
        cursor.close()
    return render_template("editEmployee.html",result=result,url=url)

@app.route("/editemp",methods=['POST','GET'])
def EditEmp():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    phone = request.form['phone']
    position = request.form['position']
    department = request.form['department']
    salary = request.form['salary']
    emp_image_file = request.files['emp_image_file']

    emp_name = "" + first_name + " " + last_name
    update_sql = "UPDATE employee set first_name =  %s , last_name = %s , email =  %s, phone =  %s , position = %s , department =  %s, salary =  %s WHERE emp_id =  %s"
    cursor = db_conn.cursor()

    try:

        cursor.execute(update_sql, ( first_name, last_name, email, phone,position,department,salary,emp_id))
        db_conn.commit()
        
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')
        if emp_image_file.filename != "":
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
    return render_template('message.html',alert=True,edit=True,name=emp_name)

@app.route("/calculate" ,methods=['POST','GET'])
def calculateNetSalary():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    select_emp = "SELECT * FROM employee WHERE emp_id = %(emp_id)s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_emp, {'emp_id': int(emp_id)})
        for result in cursor:
            print(result)
        
    except Exception as e:
        db_conn.rollback()
        return str(e)  

    finally:
        cursor.close()  
        if(int(result[7])!= 0 ):
            employeeEpf = int(result[7]) * 11 / 100
            employerEpf = int(result[7]) * 13 / 100
            employeeSocso,employerSocso = calculateSocso(int(result[7]))
            employeeEIS,employerEIS = calculateEIS(int(result[7]))
            net = int(result[7]) - employeeEpf - employeeSocso - employeeEIS
            totalEmployee = employeeEpf + employeeSocso + employeeEIS
            totalEmployer = employerEpf + employerSocso + employerEIS
        else:
            employeeEpf = 0
            employerEpf = 0
            employeeEIS = 0
            employerEIS = 0
            employeeSocso = 0
            employerSocso = 0
            net = 0  
        


        return render_template("calculateSalary.html",result=result,totalEmployee=totalEmployee,totalEmployer=totalEmployer,employeeEIS=employeeEIS,employerEIS=employerEIS,employeeEpf=employeeEpf,employerEpf=employerEpf,net=net,employeeSocso=employeeSocso,employerSocso=employerSocso) 

def calculateSocso(result):
    if(result > 4900):
        employerSocso = 86.65
        employeeSocso = 24.75
    elif(result > 4800):
        employerSocso = 84.85
        employeeSocso = 24.25
    elif(result > 4700):
        employerSocso = 83.15
        employeeSocso = 23.75
    elif(result > 4600):
        employerSocso = 81.35
        employeeSocso = 23.25
    elif(result > 4500):
        employerSocso = 79.65
        employeeSocso = 22.75
    elif(result > 4400):
        employerSocso = 77.85
        employeeSocso = 22.25
    elif(result > 4300):
        employerSocso = 76.15
        employeeSocso = 21.75
    elif(result > 4200):
        employerSocso = 74.35
        employeeSocso = 21.25
    elif(result > 4100):
        employerSocso = 72.65
        employeeSocso = 20.75
    elif(result > 4000):
        employerSocso = 70.85
        employeeSocso = 20.25
    elif(result > 3900):
        employerSocso = 69.15
        employeeSocso = 19.75
    elif(result > 3800):
        employerSocso = 67.35
        employeeSocso = 19.25
    elif(result > 3700):
        employerSocso = 65.65
        employeeSocso = 18.75
    elif(result > 3600):
        employerSocso = 63.85
        employeeSocso = 18.25
    elif(result > 3500):
        employerSocso = 62.15
        employeeSocso = 17.75
    elif(result > 3400):
        employerSocso = 60.35
        employeeSocso = 17.25
    elif(result > 3300):
        employerSocso = 58.65
        employeeSocso = 16.75
    elif(result > 3200):
        employerSocso = 56.85
        employeeSocso = 16.25
    elif(result > 3100):
        employerSocso = 55.15
        employeeSocso = 15.75
    elif(result > 3000):
        employerSocso = 53.35
        employeeSocso = 15.25
    elif(result > 2900):
        employerSocso = 51.65
        employeeSocso = 14.75
    elif(result > 2800):
        employerSocso = 49.85
        employeeSocso = 14.25
    elif(result > 2700):
        employerSocso = 48.15
        employeeSocso = 13.75
    elif(result > 2600):
        employerSocso = 46.35
        employeeSocso = 13.25
    elif(result > 2500):
        employerSocso = 44.65
        employeeSocso = 12.75
    elif(result > 2400):
        employerSocso = 42.85
        employeeSocso = 12.25
    elif(result > 2300):
        employerSocso = 41.15
        employeeSocso = 11.75
    elif(result > 2200):
        employerSocso = 39.35
        employeeSocso = 11.25
    elif(result > 2100):
        employerSocso = 37.65
        employeeSocso = 10.75
    elif(result > 2000):
        employerSocso = 35.85
        employeeSocso = 10.25
    elif(result > 1900):
        employerSocso = 34.15
        employeeSocso = 9.75
    elif(result > 1800):
        employerSocso = 32.35
        employeeSocso = 9.25
    elif(result > 1700):
        employerSocso = 30.65
        employeeSocso = 8.75
    elif(result > 1600):
        employerSocso = 28.85
        employeeSocso = 8.25
    elif(result > 1500):
        employerSocso = 27.15
        employeeSocso = 7.75
    elif(result > 1400):
        employerSocso = 25.35
        employeeSocso = 7.25
    elif(result > 1300):
        employerSocso = 23.65
        employeeSocso = 6.75
    elif(result > 1200):
        employerSocso = 21.85
        employeeSocso = 6.25
    elif(result > 1100):
        employerSocso = 20.15
        employeeSocso = 5.75
    elif(result > 1000):
        employerSocso = 18.35
        employeeSocso = 5.25
    elif(result > 900):
        employerSocso = 16.65
        employeeSocso = 4.75
    elif(result > 800):
        employerSocso = 14.85
        employeeSocso = 4.25
    elif(result > 700):
        employerSocso = 13.15
        employeeSocso = 3.75
    elif(result > 600):
        employerSocso = 11.35
        employeeSocso = 3.25
    elif(result > 500):
        employerSocso = 9.65
        employeeSocso = 2.75
    elif(result > 400):
        employerSocso = 7.85
        employeeSocso = 2.25
    elif(result > 300):
        employerSocso = 6.15
        employeeSocso = 1.75
    elif(result > 200):
        employerSocso = 4.35
        employeeSocso = 1.25
    elif(result > 140):
        employerSocso = 2.95
        employeeSocso = 0.85
    elif(result > 100):
        employerSocso = 2.10
        employeeSocso = 0.60
    elif(result > 70):
        employerSocso = 1.50
        employeeSocso = 0.40
    elif(result > 50):
        employerSocso = 1.10
        employeeSocso = 0.30
    elif(result > 30):
        employerSocso = 0.70
        employeeSocso = 0.20
    else:
        employerSocso = 0.40
        employeeSocso = 0.10
    return employeeSocso,employerSocso

def calculateEIS(result):
    if(result > 4900):
        employerEIS = 9.90
        employeeEIS = 9.90
    elif(result > 4800):
        employerEIS = 9.70
        employeeEIS = 9.70
    elif(result > 4700):
        employerEIS = 9.50
        employeeEIS = 9.50
    elif(result > 4600):
        employerEIS = 9.30
        employeeEIS = 9.30
    elif(result > 4500):
        employerEIS = 9.10
        employeeEIS = 9.10
    elif(result > 4400):
        employerEIS = 8.90
        employeeEIS = 8.90
    elif(result > 4300):
        employerEIS = 8.70
        employeeEIS = 8.70
    elif(result > 4200):
        employerEIS = 8.50
        employeeEIS = 8.50
    elif(result > 4100):
        employerEIS = 8.30
        employeeEIS = 8.30
    elif(result > 4000):
        employerEIS = 8.10
        employeeEIS = 8.10
    elif(result > 3900):
        employerEIS = 7.90
        employeeEIS = 7.90
    elif(result > 3800):
        employerEIS = 7.70
        employeeEIS = 7.70
    elif(result > 3700):
        employerEIS = 7.50
        employeeEIS = 7.50
    elif(result > 3600):
        employerEIS = 7.30
        employeeEIS = 7.30
    elif(result > 3500):
        employerEIS = 7.10
        employeeEIS = 7.10
    elif(result > 3400):
        employerEIS = 6.90
        employeeEIS = 6.90
    elif(result > 3300):
        employerEIS = 6.70
        employeeEIS = 6.70
    elif(result > 3200):
        employerEIS = 6.50
        employeeEIS = 6.50
    elif(result > 3100):
        employerEIS = 6.30
        employeeEIS = 6.30
    elif(result > 3000):
        employerEIS = 6.10
        employeeEIS = 6.10
    elif(result > 2900):
        employerEIS = 5.90
        employeeEIS = 5.90
    elif(result > 2800):
        employerEIS = 5.70
        employeeEIS = 5.70
    elif(result > 2700):
        employerEIS = 5.50
        employeeEIS = 5.50
    elif(result > 2600):
        employerEIS = 5.30
        employeeEIS = 5.30
    elif(result > 2500):
        employerEIS = 5.10
        employeeEIS = 5.10
    elif(result > 2400):
        employerEIS = 4.90
        employeeEIS = 4.90
    elif(result > 2300):
        employerEIS = 4.70
        employeeEIS = 4.70
    elif(result > 2200):
        employerEIS = 4.50
        employeeEIS = 4.50
    elif(result > 2100):
        employerEIS = 4.30
        employeeEIS = 4.30
    elif(result > 2000):
        employerEIS = 4.10
        employeeEIS = 4.10
    elif(result > 1900):
        employerEIS = 3.90
        employeeEIS = 3.90
    elif(result > 1800):
        employerEIS = 3.70
        employeeEIS = 3.70
    elif(result > 1700):
        employerEIS = 3.50
        employeeEIS = 3.50
    elif(result > 1600):
        employerEIS = 3.30
        employeeEIS = 3.30
    elif(result > 1500):
        employerEIS = 3.10
        employeeEIS = 3.10
    elif(result > 1400):
        employerEIS = 2.90
        employeeEIS = 2.90
    elif(result > 1300):
        employerEIS = 2.70
        employeeEIS = 2.70
    elif(result > 1200):
        employerEIS = 2.50
        employeeEIS = 2.50
    elif(result > 1100):
        employerEIS = 2.30
        employeeEIS = 2.30
    elif(result > 1000):
        employerEIS = 2.10
        employeeEIS = 2.10
    elif(result > 900):
        employerEIS = 1.90
        employeeEIS = 1.90
    elif(result > 800):
        employerEIS = 1.70
        employeeEIS = 1.70
    elif(result > 700):
        employerEIS = 1.50
        employeeEIS = 1.50
    elif(result > 600):
        employerEIS = 1.30
        employeeEIS = 1.30
    elif(result > 500):
        employerEIS = 1.10
        employeeEIS = 1.10
    elif(result > 400):
        employerEIS = 0.90
        employeeEIS = 0.90
    elif(result > 300):
        employerEIS = 0.70
        employeeEIS = 0.70
    elif(result > 200):
        employerEIS = 0.50
        employeeEIS = 0.50
    elif(result > 140):
        employerEIS = 0.35
        employeeEIS = 0.35
    elif(result > 100):
        employerEIS = 0.25
        employeeEIS = 0.25
    elif(result > 70):
        employerEIS = 0.20
        employeeEIS = 0.20
    elif(result > 50):
        employerEIS = 0.15
        employeeEIS = 0.15
    elif(result > 30):
        employerEIS = 0.10
        employeeEIS = 0.10
    else:
        employerEIS = 0.05
        employeeEIS = 0.05
    return employeeEIS,employerEIS

@app.template_filter('conv_curr')
def conv_curr(amount): 
    import locale
    locale.setlocale(locale.LC_ALL, 'ms_MY') 
    return locale.currency(amount)

@app.route("/addLeave",methods=['POST','GET'])
def applyLeave():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    reason = request.form['reason']
    start_date = request.form['startDate']
    end_date = request.form['endDate']
    emp_image_file = request.files['supportDocument']

    insert_sql = "INSERT INTO employee.leave VALUES (%s,%s,%s,%s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, reason,start_date,end_date))
        db_conn.commit()
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_LeaveDocument_" + start_date
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
    return render_template('message.html',alert=True,leave=True)

@app.route("/addLeave/", methods=['GET', 'POST'])
def addLeave():
    
    emp_id = request.form['emp_id']
    return render_template('addLeave.html',emp_id=emp_id)

@app.route("/checkInAttendance/",methods=['GET','POST'])
def checkIn():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']

    #UPDATE STATEMENT
    update_stmt= "UPDATE employee SET checkIn =(%(checkIn)s) WHERE emp_id = %(emp_id)s"

    cursor = db_conn.cursor()

    LoginTime = datetime.now()
    formatted_login = LoginTime.strftime('%Y-%m-%d %H:%M:%S')
    print ("Check in time:{}",formatted_login)

    try:
        cursor.execute(update_stmt, { 'checkIn': formatted_login ,'emp_id':int(emp_id)})
        db_conn.commit()
        print(" Data Updated into MySQL")

    except Exception as e:
        return str(e)

    finally:
        cursor.close()
        
    return render_template("message.html",LoginTime=formatted_login,alert=True,checkIn=True)

@app.route("/checkOutAttendance/",methods=['GET','POST'])
def checkOut():
    db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
    emp_id = request.form['emp_id']
    # SELECT STATEMENT TO GET DATA FROM MYSQL
    select_stmt = "SELECT checkIn FROM employee WHERE emp_id = %(emp_id)s"
    insert_statement="INSERT INTO attendance VALUES (%s,%s,%s,%s)"
    update_stmt= "UPDATE employee SET checkIn =%s WHERE emp_id = %s"

    cursor = db_conn.cursor()
    try:
        
        cursor.execute(select_stmt,{'emp_id':int(emp_id)})
        LoginTime= cursor
       
        for row in LoginTime:
            formatted_login = row
            print(formatted_login[0])
        CheckoutTime=datetime.now()
        LogininDate = datetime.strptime(formatted_login[0],'%Y-%m-%d %H:%M:%S')
        formatted_checkout = CheckoutTime.strftime('%Y-%m-%d %H:%M:%S')
        Total_Working_Hours = CheckoutTime - LogininDate
        print(Total_Working_Hours)
        try:
            cursor.execute(insert_statement,(emp_id,formatted_login[0],formatted_checkout,Total_Working_Hours))
            db_conn.commit()
            print(" Data Inserted into MySQL")
            try:
                LoginTime = "0000-00-00 00:00:00"
                cursor.execute(update_stmt,(LoginTime,emp_id))
                db_conn.commit()
                print(" Data Updated into MySQL")

            except Exception as e:
                return str(e)

            finally:
                cursor.close()
                return render_template("attendance.html",emp_id = emp_id ,Checkout = formatted_checkout,LoginTime=formatted_login[0],TotalWorkingHours=Total_Working_Hours)
        except Exception as e:
            return str(e)
    except Exception as e:
        return str(e)       

            


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
