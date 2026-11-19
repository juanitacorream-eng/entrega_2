import os
import json

# --- Configuración de directorios y archivos ---
os.makedirs("server/labs", exist_ok=True)
usersFile = "server/users.txt"
sessionsFile = "server/sessions.txt"
assignmentsFile = "server/assignments.txt"

# Crear archivos base si no existen
for f in [usersFile, sessionsFile, assignmentsFile]:
    if not os.path.exists(f):
        open(f, 'w').close()

def getUser(user_id):
    target_id = str(user_id).strip()
    with open(usersFile, "r") as file:
        for line in file:
            if line.strip():
                user = json.loads(line.strip())
                if str(user.get("id", "")).strip() == target_id:
                    return user
    return None

def isLoggedIn(user_id):
    target_id = str(user_id).strip()
    with open(sessionsFile, "r") as file:
        return target_id in [line.strip() for line in file if line.strip()]

def registerUser(name, id, role, password):
    if getUser(id):
        return "User already registered"
    user_data = {"name": str(name).strip(), "id": str(id).strip(), "role": str(role).strip(), "password": str(password).strip()}
    with open(usersFile, "a") as file:
        file.write(json.dumps(user_data) + "\n")
    return f"User {name} with role {role} registered"

def openSession(id, password):
    user = getUser(id)
    if user and user["password"] == str(password).strip():
        if not isLoggedIn(id):
            with open(sessionsFile, "a") as file:
                file.write(str(id).strip() + "\n")
        return "Session was succesfully opened"
    return "error"

def closeSession(id):
    if not isLoggedIn(id):
        return "error"
    with open(sessionsFile, "r") as file:
        sessions = [line.strip() for line in file if line.strip()]
    target_id = str(id).strip()
    if target_id in sessions:
        sessions.remove(target_id)
    with open(sessionsFile, "w") as file:
        for session in sessions:
            file.write(session + "\n")
    return "Session was succesfully closed"

def uploadLab(id, file_name, file_data):
    user = getUser(id)
    if user and user["role"] == "professor" and isLoggedIn(id):
        target_path = os.path.join("server/labs", str(file_name).strip())
        with open(target_path, "wb") as f:
            f.write(file_data)
        return "File was succesfully received"
    return "error"

def downloadLab(id, file_name):
    user = getUser(id)
    if user and user["role"] == "student" and isLoggedIn(id):
        lab_name = str(file_name).replace(".zip", "").strip()
        is_assigned = False
        with open(assignmentsFile, "r") as file:
            for line in file:
                if line.strip():
                    assignment = json.loads(line.strip())
                    if assignment["student_id"] == str(id).strip() and assignment["lab_name"] == lab_name:
                        is_assigned = True
                        break
        if is_assigned:
            file_path = os.path.join("server/labs", str(file_name).strip())
            try:
                with open(file_path, "rb") as f:
                    return f.read()
            except FileNotFoundError:
                pass
    return "error"

def listStudentLabs(id):
    user = getUser(id)
    if user and user["role"] == "student" and isLoggedIn(id):
        assigned_labs = []
        with open(assignmentsFile, "r") as file:
            for line in file:
                if line.strip():
                    assignment = json.loads(line.strip())
                    if assignment["student_id"] == str(id).strip():
                        assigned_labs.append(assignment["lab_name"])
        if not assigned_labs:
            return "No labs assigned"
        return "\n".join(assigned_labs)
    return "error"

def listProfessorsLabs(id):
    user = getUser(id)
    if user and user["role"] == "professor" and isLoggedIn(id):
        try:
            labs = os.listdir("server/labs")
            return "\n".join(labs) if labs else "No labs uploaded"
        except Exception:
            pass
    return "error"

def listStudents(id):
    user = getUser(id)
    if user and user["role"] == "professor" and isLoggedIn(id):
        students = []
        with open(usersFile, "r") as file:
            for line in file:
                if line.strip():
                    u = json.loads(line.strip())
                    if u["role"] == "student":
                        students.append(f"{u['name']}, {u['id']}")
        return "\n".join(students) if students else "No students registered"
    return "error"

def assignLab(id, lab_name, student_id):
    user = getUser(id)
    student = getUser(student_id)
    
    # Validaciones robustas
    if user and user["role"] == "professor" and isLoggedIn(id):
        if student and student["role"] == "student":
            
            assignment_data = {
                "student_id": str(student_id).strip(),
                "lab_name": str(lab_name).strip()
            }
            with open(assignmentsFile, "a") as file:
                file.write(json.dumps(assignment_data) + "\n")
                
            return "Lab assigned successfully"
            
    return "error"
