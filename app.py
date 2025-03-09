from flask import Flask, render_template, request, jsonify
from datetime import datetime, date
from collections import deque

app = Flask(__name__)

students = [
    "Ansh", "Falak", "Anirudh", "Jay", "Hemang",
    "Rohan", "Mehak", "Ishaan", "Aditi", "Karan",
    "Neha", "Rahul", "Simran", "Vivek", "Priya",
    "Siddharth", "Tanya", "Arjun", "Sakshi", "Manav"
]

slots = {
    "DSA": "9 AM - 11 AM",
    "MERN STACK": "12 PM - 2 PM",
    "AI/ML": "2:30 PM - 4:40 PM"
}

attendance_records = {}

attendance_queue = deque()
sign_out_queue = deque()

@app.route("/")
def home():
    return render_template("index.html", students=students, slots=slots)

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    """Marks attendance for the selected student in a specific slot with timestamp."""
    today = date.today().strftime("%Y-%m-%d")
    student_name = request.form.get("student")
    slot = request.form.get("slot")
    timestamp = datetime.now().strftime("%H:%M:%S")

    if not student_name or slot not in slots:
        return jsonify({"status": "error", "message": "Invalid student or slot"})

    if today not in attendance_records:
        attendance_records[today] = {}
    
    if slot not in attendance_records[today]:
        attendance_records[today][slot] = {}

    if student_name not in attendance_records[today][slot]:
        attendance_queue.append((student_name, slot, timestamp))
        while attendance_queue:
            student, selected_slot, time = attendance_queue.popleft()
            attendance_records[today][selected_slot][student] = {"status": "Present", "time": time}
            sign_out_queue.append((student, selected_slot))
            return jsonify({"status": "success", "message": f"{student} marked present at {time} for {selected_slot} ({today})"})

    return jsonify({"status": "error", "message": f"{student_name} is already marked present for {slot}"})

@app.route("/sign_out", methods=["POST"])
def sign_out():
    """Signs out the student from a specific slot with timestamp."""
    today = date.today().strftime("%Y-%m-%d")
    student_name = request.form.get("student")
    slot = request.form.get("slot")
    timestamp = datetime.now().strftime("%H:%M:%S")

    if not student_name or slot not in slots or student_name not in attendance_records.get(today, {}).get(slot, {}):
        return jsonify({"status": "error", "message": "Invalid student, slot, or not marked present"})

    if (student_name, slot) in sign_out_queue:
        sign_out_queue.remove((student_name, slot))
        attendance_records[today][slot][student_name] = {"status": "Signed Out", "time": timestamp}
        return jsonify({"status": "success", "message": f"{student_name} signed out at {timestamp} from {slot} on {today}"})

    return jsonify({"status": "error", "message": "Already signed out"})

@app.route("/get_attendance", methods=["GET"])
def get_attendance():
    """Returns the attendance records."""
    return jsonify(attendance_records)

if __name__ == "__main__":
    app.run(debug=True)
