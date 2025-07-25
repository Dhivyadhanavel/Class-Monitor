-- Create Database

CREATE DATABASE IF NOT EXISTS class_admin;
USE class_admin;

-- Student Table
DROP TABLE IF EXISTS Student;
CREATE TABLE  Student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE,
    contact_number VARCHAR(15),
    email VARCHAR(50)
   
);

-- Class Table
DROP TABLE IF EXISTS Class;
CREATE TABLE Class (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    teacher_name VARCHAR(255),
    subject VARCHAR(255)
);


-- Attendance Table
DROP TABLE IF EXISTS Attendance;
CREATE TABLE  Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    class_id INT,
    date DATE,
    is_present BOOLEAN,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES Class(class_id) ON DELETE CASCADE
);


-- Participation Table
DROP TABLE IF EXISTS Participation;
CREATE TABLE  Participation (
    participation_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    class_id INT,
    participation_score INT,
    date DATE,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES Class(class_id) ON DELETE CASCADE
);

-- Grades Table
DROP TABLE IF EXISTS Grades;
CREATE TABLE  Grades (
    grade_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    class_id INT,
    assignment_type VARCHAR(50),
    score FLOAT,
    FOREIGN KEY (student_id) REFERENCES Student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES Class(class_id) ON DELETE CASCADE
);


-- Function to Calculate Attendance Rate
DROP FUNCTION IF EXISTS CalculateAttendanceRate;
CREATE FUNCTION CalculateAttendanceRate(input_student_id INT) 
RETURNS FLOAT
DETERMINISTIC
BEGIN
    DECLARE attendance_rate FLOAT DEFAULT 0;
    DECLARE total_classes INT DEFAULT 0;
    DECLARE attended_classes INT DEFAULT 0;
    
    -- Calculate total distinct dates in Attendance table for all classes
    SELECT COUNT(DISTINCT date) INTO total_classes FROM Attendance WHERE class_id IN (SELECT class_id FROM Class);

    -- Calculate attended classes for the specified student
    SELECT COUNT(*) INTO attended_classes 
    FROM Attendance 
    WHERE student_id = input_student_id AND is_present = 1;
    
    -- Calculate attendance rate and avoid division by zero
    IF total_classes > 0 THEN
        SET attendance_rate = (attended_classes / total_classes) * 100;
    END IF;
    
    RETURN attendance_rate;
END;


-- Trigger for Absence Notification
CREATE TRIGGER NotifyAbsence 
AFTER INSERT ON Attendance
FOR EACH ROW
BEGIN
    IF NEW.is_present = 0 THEN
        -- Call the stored procedure to send a notification
        CALL SendAbsenceNotification(NEW.student_id);
    END IF;
END;

-- Stored Procedure to Send Absence Notification
CREATE PROCEDURE SendAbsenceNotification(input_student_id INT)
BEGIN
    DECLARE student_email VARCHAR(50);
    DECLARE student_name VARCHAR(100);
    
    -- Retrieve student details
    SELECT email, CONCAT(first_name, ' ', last_name)
    INTO student_email, student_name
    FROM Student
    WHERE student_id = input_student_id;
    
    -- Notification simulation (replace with actual notification logic)
    SELECT CONCAT('Sending absence notification to ', student_name, ' at ', student_email) AS Notification;
END;
