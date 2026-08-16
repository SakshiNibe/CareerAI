from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)

# =========================================================
# CONFIGURATION
# =========================================================

app.config["MYSQL_HOST"] = config.MYSQL_HOST
app.config["MYSQL_USER"] = config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = config.MYSQL_DB

app.secret_key = config.SECRET_KEY

mysql = MySQL(app)


# =========================================================
# HOME / LOGIN
# =========================================================

@app.route("/")
def home():
    return render_template("login.html")


# =========================================================
# REGISTER PAGE
# =========================================================

@app.route("/register")
def register():
    return render_template("register.html")


# =========================================================
# SAVE REGISTRATION
# =========================================================

@app.route("/save", methods=["POST"])
def save():

    name = request.form["name"].strip()
    email = request.form["email"].strip()
    password = request.form["password"]
    mobile = request.form["mobile"].strip()
    branch = request.form["branch"].strip()
    cgpa = request.form["cgpa"]

    cur = mysql.connection.cursor()

    # Check existing email
    cur.execute(
        "SELECT id FROM students WHERE email=%s",
        (email,)
    )

    existing_user = cur.fetchone()

    if existing_user:

        cur.close()

        flash("Email already registered!")

        return redirect("/register")

    # Password Hashing
    hashed_password = generate_password_hash(password)

    cur.execute("""
        INSERT INTO students
        (name, email, password, mobile, branch, cgpa)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        name,
        email,
        hashed_password,
        mobile,
        branch,
        cgpa
    ))

    mysql.connection.commit()

    cur.close()

    flash("Registration Successful! Please Login.")

    return redirect("/")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"].strip()
    password = request.form["password"]

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM students WHERE email=%s",
        (email,)
    )

    user = cur.fetchone()

    cur.close()

    if not user:

        flash("Invalid Email or Password")

        return redirect("/")

    try:

        # password column = index 3
        password_valid = check_password_hash(
            user[3],
            password
        )

    except Exception:

        password_valid = False

    if password_valid:

        # name column = index 1
        session["user"] = user[1]

        return redirect("/dashboard")

    flash("Invalid Email or Password")

    return redirect("/")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template(
        "dashboard.html",
        name=session["user"]
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.")

    return redirect("/")


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM students WHERE name=%s",
        (session["user"],)
    )

    student = cur.fetchone()

    cur.close()

    if not student:
        session.clear()
        return redirect("/")

    return render_template(
        "profile.html",
        student=student
    )


# =========================================================
# UPDATE PROFILE
# =========================================================

@app.route("/update_profile", methods=["POST"])
def update_profile():

    if "user" not in session:
        return redirect("/")

    name = request.form["name"].strip()
    mobile = request.form["mobile"].strip()
    branch = request.form["branch"].strip()
    cgpa = request.form["cgpa"]

    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE students
        SET mobile=%s,
            branch=%s,
            cgpa=%s
        WHERE name=%s
    """, (
        mobile,
        branch,
        cgpa,
        name
    ))

    mysql.connection.commit()

    cur.close()

    flash("Profile Updated Successfully!")

    return redirect("/profile")


# =========================================================
# SKILLS PAGE
# =========================================================

@app.route("/skills")
def skills():

    if "user" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT id FROM students WHERE name=%s",
        (session["user"],)
    )

    student = cur.fetchone()

    if not student:

        cur.close()

        session.clear()

        return redirect("/")

    student_id = student[0]

    cur.execute(
        "SELECT * FROM skills WHERE student_id=%s",
        (student_id,)
    )

    data = cur.fetchall()

    cur.close()

    return render_template(
        "skills.html",
        skills=data
    )


# =========================================================
# ADD SKILL
# =========================================================

@app.route("/add_skill", methods=["POST"])
def add_skill():

    if "user" not in session:
        return redirect("/")

    skill = request.form["skill"].strip()

    if skill == "":
        return redirect("/skills")

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT id FROM students WHERE name=%s",
        (session["user"],)
    )

    student = cur.fetchone()

    if not student:

        cur.close()

        return redirect("/")

    student_id = student[0]

    # Check duplicate skill
    cur.execute("""
        SELECT id
        FROM skills
        WHERE student_id=%s
        AND LOWER(skill_name)=LOWER(%s)
    """, (
        student_id,
        skill
    ))

    existing_skill = cur.fetchone()

    if existing_skill:

        cur.close()

        flash("Skill already added.")

        return redirect("/skills")

    cur.execute("""
        INSERT INTO skills
        (student_id, skill_name)
        VALUES (%s, %s)
    """, (
        student_id,
        skill
    ))

    mysql.connection.commit()

    cur.close()

    return redirect("/skills")


# =========================================================
# DELETE SKILL
# =========================================================

@app.route("/delete_skill/<int:id>")
def delete_skill(id):

    if "user" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute(
        "DELETE FROM skills WHERE id=%s",
        (id,)
    )

    mysql.connection.commit()

    cur.close()

    return redirect("/skills")


# =========================================================
# CAREER RECOMMENDATION
# =========================================================

@app.route("/career")
def career():

    if "user" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT id FROM students WHERE name=%s",
        (session["user"],)
    )

    student = cur.fetchone()

    if not student:

        cur.close()

        return redirect("/")

    student_id = student[0]

    cur.execute(
        "SELECT skill_name FROM skills WHERE student_id=%s",
        (student_id,)
    )

    data = cur.fetchall()

    cur.close()

    # Convert skills to lowercase
    skills = [
        s[0].strip().lower()
        for s in data
    ]

    recommendation = "Add More Skills"

    # =====================================================
    # CAREER RULES
    # =====================================================

    if "python" in skills:

        if "flask" in skills or "django" in skills:

            recommendation = "Python Backend Developer"

        elif "machine learning" in skills:

            recommendation = "Machine Learning Engineer"

        elif "pandas" in skills or "numpy" in skills:

            recommendation = "Data Analyst"

        else:

            recommendation = "Python Developer"


    elif "java" in skills:

        if "spring" in skills or "spring boot" in skills:

            recommendation = "Java Backend Developer"

        else:

            recommendation = "Java Developer"


    elif "react" in skills and "javascript" in skills:

        recommendation = "React Developer"


    elif (
        "html" in skills
        and "css" in skills
        and "javascript" in skills
    ):

        recommendation = "Frontend Developer"


    elif "c++" in skills:

        recommendation = "Software Engineer"


    elif "sql" in skills or "mysql" in skills:

        recommendation = "Database Developer"


    return render_template(
        "career.html",
        skills=skills,
        career=recommendation
    )


# =========================================================
# PLACEMENT PREDICTION
# =========================================================

@app.route("/placement")
def placement():

    if "user" not in session:
        return redirect("/")

    cur = mysql.connection.cursor()

    # Student details
    cur.execute("""
        SELECT id, cgpa
        FROM students
        WHERE name=%s
    """, (
        session["user"],
    ))

    student = cur.fetchone()

    if not student:

        cur.close()

        return redirect("/")

    student_id = student[0]

    try:
        cgpa = float(student[1])
    except:
        cgpa = 0.0


    # Total skills
    cur.execute("""
        SELECT COUNT(*)
        FROM skills
        WHERE student_id=%s
    """, (
        student_id,
    ))

    total_skills = cur.fetchone()[0]

    cur.close()


    # =====================================================
    # PLACEMENT PREDICTION
    # =====================================================

    if cgpa >= 8.5 and total_skills >= 5:

        result = "High Chance"
        color = "green"

    elif cgpa >= 7.0 and total_skills >= 3:

        result = "Medium Chance"
        color = "orange"

    else:

        result = "Low Chance"
        color = "red"


    return render_template(
        "placement.html",
        cgpa=cgpa,
        skills=total_skills,
        result=result,
        color=color
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("--------------------------------------")
    print("CareerAI Application Starting...")
    print("--------------------------------------")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )