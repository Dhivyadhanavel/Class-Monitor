from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from config import DB_CONFIG
from datetime import datetime

app = Flask(__name__)

# Establish database connection
db = mysql.connector.connect(**DB_CONFIG)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Student Management
@app.route('/students')
def students():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    cursor.close()
    return render_template('students.html', students=students)

@app.route('/students/add', methods=['POST'])
def add_student():
    data = request.form
    cursor = db.cursor()
    cursor.execute("INSERT INTO Student (first_name, last_name, dob, contact_number, email) VALUES (%s, %s, %s, %s, %s)", 
                   (data['first_name'], data['last_name'], data['dob'], data['contact_number'], data['email']))
    db.commit()
    cursor.close()
    return redirect(url_for('students'))

@app.route('/students/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM Attendance WHERE student_id = %s", (student_id,))
    cursor.execute("DELETE FROM Participation WHERE student_id = %s", (student_id,))
    cursor.execute("DELETE FROM Grades WHERE student_id = %s", (student_id,))
    cursor.execute("DELETE FROM Student WHERE student_id = %s", (student_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('students'))

@app.route('/classes')
def classes():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Class")
    classes = cursor.fetchall()
    cursor.close()
    return render_template('classes.html', classes=classes)
        
@app.route('/classes/add', methods=['POST'])
def add_class():
    data = request.form
    cursor = db.cursor()
    cursor.execute("INSERT INTO Class (class_name, teacher_name, subject) VALUES (%s, %s, %s)", 
                   (data['class_name'], data['teacher_name'], data['subject']))
    db.commit()
    cursor.close()
    return redirect(url_for('classes'))

@app.route('/classes/delete/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM Class WHERE class_id = %s", (class_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('classes'))


# Attendance Management
@app.route('/attendance')
def attendance():
    cursor = db.cursor(dictionary=True)
    
    # Get all attendance records for viewing
    cursor.execute("""
        SELECT Attendance.student_id, Attendance.class_id, Attendance.date, Attendance.is_present, 
               Class.class_name, Student.first_name, Student.last_name 
        FROM Attendance
        JOIN Class ON Attendance.class_id = Class.class_id
        JOIN Student ON Attendance.student_id = Student.student_id
    """)
    attendance_records = cursor.fetchall()
    
    # Fetch students for the dropdown
    cursor.execute("SELECT student_id, first_name, last_name FROM Student")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM Class")
    classes = cursor.fetchall()

    # Fetch classes for the dropdown
    cursor.execute("SELECT class_id, class_name FROM Class")
    classes = cursor.fetchall()
    
    cursor.close()
    
    return render_template('attendance.html', attendance=attendance_records, students=students, classes=classes)


@app.route('/attendance/add', methods=['POST'])
def add_attendance():
    data = request.form
    is_present = 1 if 'is_present' in data else 0  # Checkbox handling
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO Attendance (student_id, class_id, date, is_present) 
        VALUES (%s, %s,%s, %s)
    """, (data['student_id'], data['class_id'], data['date'], is_present))
    db.commit()
    cursor.close()
    return redirect(url_for('attendance'))


# Participation Management

@app.route('/participation')
def participation():
    cursor = db.cursor(dictionary=True)

    # Fetching all participation records for the table
    cursor.execute("SELECT * FROM Participation")
    participation_records = cursor.fetchall()

    # Fetching students and classes for the dropdowns
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM Class")  # Assuming you have a 'Class' table
    classes = cursor.fetchall()

    cursor.close()

    return render_template('participation.html', participation=participation_records, students=students, classes=classes)


@app.route('/participation/add', methods=['POST'])
def add_participation():
    data = request.form
    cursor = db.cursor()

    # Insert participation record into the database
    cursor.execute("""
        INSERT INTO Participation (student_id, class_id, participation_score, date)
        VALUES (%s, %s, %s, %s)
    """, (data['student_id'], data['class_id'], data['participation_score'], data['date']))
    
    db.commit()
    cursor.close()
    return redirect(url_for('participation'))

# Grade Management


@app.route('/grades')
def grades():
    cursor = db.cursor(dictionary=True)

    # Get all students for the dropdown
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()

    # Get all classes for the dropdown
    cursor.execute("SELECT * FROM Class")  # Assuming there's a Class table
    classes = cursor.fetchall()

    cursor.close()

    return render_template('grades.html', students=students, classes=classes)


@app.route('/grades/add', methods=['POST'])
def add_grade():
    data = request.form
    cursor = db.cursor()

    # Insert the grade record into the Grades table
    cursor.execute("""
        INSERT INTO Grades (student_id, class_id, assignment_type, score) 
        VALUES (%s, %s, %s, %s)
    """, (data['student_id'], data['class_id'], data['assignment_type'], data['score']))

    # Commit the transaction and close the cursor
    db.commit()
    cursor.close()

    return redirect(url_for('grades'))  # Redirect to the grades page after successful submission

# Report Generation
@app.route('/report')
def report():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.first_name, s.last_name, 
               COUNT(a.attendance_id) AS total_attendance,
               SUM(CASE WHEN a.is_present = 1 THEN 1 ELSE 0 END) AS present_days,
               (SUM(CASE WHEN a.is_present = 1 THEN 1 ELSE 0 END) / COUNT(a.attendance_id)) * 100 AS attendance_rate
        FROM Student s
        LEFT JOIN Attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id;
    """)
    report_data = cursor.fetchall()
    cursor.close()
    
    return render_template('report.html', report=report_data)



if __name__ == '__main__':
    app.run(debug=True)
