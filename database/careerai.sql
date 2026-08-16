CREATE TABLE skills(
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    skill_name VARCHAR(100),
    FOREIGN KEY(student_id) REFERENCES students(id)
);