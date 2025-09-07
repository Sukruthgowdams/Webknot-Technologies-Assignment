from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
from flask import Flask, render_template
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- MODELS --------------------
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    event_type = db.Column(db.String, default='Workshop')
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    registrations = db.relationship('Registration', backref='event', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='event', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='event', lazy=True, cascade='all, delete-orphan')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    registrations = db.relationship('Registration', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='student', lazy=True, cascade='all, delete-orphan')

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('event_id', 'student_id', name='u_event_student'),)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    present = db.Column(db.Integer, default=0)  # 1 = present
    checked_in_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    rating = db.Column(db.Integer)
    comments = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------- INIT DB --------------------
with app.app_context():
    db.create_all()

# -------------------- HELPERS --------------------
def iso(dt):
    return dt.isoformat() if dt else None

# -------------------- ROUTES --------------------
# -------------------- ROUTES --------------------
@app.route('/', defaults={'path': ''})
@app.route('/ui', defaults={'path': ''})
def serve_ui(path):
    return render_template('index.html')


# ---------- Events ----------
@app.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    result = []
    for e in events:
        result.append({
            "id": e.id,
            "title": e.title,
            "event_type": e.event_type,
            "start_time": iso(e.start_time),
            "end_time": iso(e.end_time),
            "registrations": len(e.registrations)
        })
    return jsonify(result), 200

@app.route('/events', methods=['POST'])
def create_event():
    data = request.get_json() or {}
    title = data.get('title')
    if not title:
        return jsonify({"error": "title is required"}), 400
    try:
        start_time = datetime.fromisoformat(data['start_time']) if data.get('start_time') else None
        end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else None
    except ValueError:
        return jsonify({"error": "invalid date format - use ISO format"}), 400

    e = Event(title=title, event_type=data.get('event_type', 'Workshop'), start_time=start_time, end_time=end_time)
    db.session.add(e)
    db.session.commit()
    return jsonify({"id": e.id, "message": "event created"}), 201

@app.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    e = Event.query.get_or_404(event_id)
    return jsonify({
        "id": e.id,
        "title": e.title,
        "event_type": e.event_type,
        "start_time": iso(e.start_time),
        "end_time": iso(e.end_time),
        "registrations": [
            {
                "registration_id": r.id,
                "student_id": r.student.id,
                "student": r.student.name,
                "email": r.student.email
            }
            for r in e.registrations
        ]
    }), 200

@app.route('/events/<int:event_id>/students', methods=['GET'])
def get_event_students(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "event not found"}), 404
    students = []
    for r in event.registrations:
        s = r.student
        students.append({"student_id": s.id, "name": s.name, "email": s.email, "registration_id": r.id})
    return jsonify(students), 200

@app.route('/events', methods=['DELETE'])
def delete_all_events():
    num_deleted = Event.query.delete()
    db.session.commit()
    return jsonify({"message": f"Deleted {num_deleted} events"}), 200

# ---------- Students ----------
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({"error": "name and email required"}), 400
    existing = Student.query.filter_by(email=email).first()
    if existing:
        return jsonify({"id": existing.id, "name": existing.name, "email": existing.email, "message": "already exists"}), 200
    student = Student(name=name, email=email)
    db.session.add(student)
    db.session.commit()
    return jsonify({"id": student.id, "name": student.name, "email": student.email}), 201

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{"id": s.id, "name": s.name, "email": s.email} for s in students]), 200

@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "student not found"}), 404
    return jsonify({"id": student.id, "name": student.name, "email": student.email}), 200

@app.route('/students/<int:student_id>/events', methods=['GET'])
def get_student_events(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "student not found"}), 404
    events = []
    for r in student.registrations:
        e = r.event
        events.append({
            "event_id": e.id,
            "title": e.title,
            "event_type": e.event_type,
            "start_time": iso(e.start_time),
            "end_time": iso(e.end_time),
            "registration_id": r.id
        })
    return jsonify(events), 200

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return jsonify({"error": "student not found"}), 404
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "student deleted"}), 200

# ---------- Registrations / Attendance / Feedback ----------
@app.route('/events/<int:event_id>/register', methods=['POST'])
def register_student(event_id):
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "event not found"}), 404

    student = Student.query.filter_by(email=email).first()
    if not student:
        student = Student(name=name, email=email)
        db.session.add(student)
        db.session.commit()

    reg = Registration.query.filter_by(event_id=event_id, student_id=student.id).first()
    if reg:
        return jsonify({"message": "already registered", "registration_id": reg.id}), 200

    reg = Registration(event_id=event_id, student_id=student.id)
    db.session.add(reg)
    db.session.commit()
    return jsonify({"message": "registered", "registration_id": reg.id}), 201

@app.route('/events/<int:event_id>/attendance', methods=['POST'])
def mark_attendance(event_id):
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({"error": "email is required"}), 400

    student = Student.query.filter_by(email=email).first()
    if not student:
        return jsonify({"error": "student not found"}), 404

    reg = Registration.query.filter_by(event_id=event_id, student_id=student.id).first()
    if not reg:
        return jsonify({"error": "student not registered for this event"}), 400

    attendance = Attendance.query.filter_by(event_id=event_id, student_id=student.id).first()
    if not attendance:
        attendance = Attendance(event_id=event_id, student_id=student.id, present=1)
        db.session.add(attendance)
    else:
        attendance.present = 1
        attendance.checked_in_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "attendance marked"}), 200

@app.route('/events/<int:event_id>/feedback', methods=['POST'])
def submit_feedback(event_id):
    data = request.get_json() or {}
    # accept either student_id or email for convenience
    student_id = data.get('student_id')
    email = data.get('email')

    if not student_id and not email:
        return jsonify({"error": "student_id or email is required"}), 400

    student = None
    if student_id:
        student = Student.query.get(student_id)
    else:
        student = Student.query.filter_by(email=email).first()

    if not student:
        return jsonify({"error": "student not found"}), 404

    try:
        rating = int(data.get('rating', 0))
    except (ValueError, TypeError):
        return jsonify({"error": "rating must be a number"}), 400
    if rating < 1 or rating > 5:
        return jsonify({"error": "rating must be 1-5"}), 400

    reg = Registration.query.filter_by(event_id=event_id, student_id=student.id).first()
    if not reg:
        return jsonify({"error": "student not registered for this event"}), 400

    existing_feedback = Feedback.query.filter_by(event_id=event_id, student_id=student.id).first()
    if existing_feedback:
        return jsonify({"error": "feedback already submitted"}), 400

    feedback = Feedback(event_id=event_id, student_id=student.id, rating=rating, comments=data.get('comments'))
    db.session.add(feedback)
    db.session.commit()
    return jsonify({"message": "feedback saved"}), 201

# Convenience endpoints for deleting registrations/feedback/attendance
@app.route('/registrations', methods=['DELETE'])
def delete_all_registrations():
    num_deleted = Registration.query.delete()
    db.session.commit()
    return jsonify({"message": f"Deleted {num_deleted} registrations"}), 200

@app.route('/attendance', methods=['DELETE'])
def delete_all_attendance():
    num_deleted = Attendance.query.delete()
    db.session.commit()
    return jsonify({"message": f"Deleted {num_deleted} attendance records"}), 200

@app.route('/feedbacks', methods=['DELETE'])
def delete_all_feedbacks():
    num_deleted = Feedback.query.delete()
    db.session.commit()
    return jsonify({"message": f"Deleted {num_deleted} feedbacks"}), 200

# -------------------- REPORTS (ORM) --------------------

@app.route('/reports/event-popularity')
def event_popularity():
    event_type = request.args.get('type')
    query = db.session.query(
        Event.id, Event.title, Event.event_type, Event.start_time, Event.end_time,
        func.count(Registration.id).label('registrations')
    ).outerjoin(Registration).group_by(Event.id).order_by(func.count(Registration.id).desc())

    if event_type:
        query = query.filter(Event.event_type == event_type)

    data = [
        dict(
            id=e.id,
            title=e.title,
            event_type=e.event_type,
            start_time=iso(e.start_time),
            end_time=iso(e.end_time),
            registrations=e.registrations
        )
        for e in query.all()
    ]
    return jsonify(data), 200


@app.route('/reports/attendance-percentage')
def attendance_percentage():
    events = Event.query.all()
    data = []
    for e in events:
        total_regs = Registration.query.filter_by(event_id=e.id).count()
        attended = Attendance.query.filter_by(event_id=e.id, present=1).count()
        data.append({
            "event_id": e.id,
            "title": e.title,
            "registered": total_regs,
            "attended": attended
        })
    return jsonify(data), 200


@app.route('/reports/average-feedback')
def average_feedback():
    query = db.session.query(
        Event.id, Event.title,
        func.avg(Feedback.rating).label('avg_rating'),
        func.count(Feedback.id).label('feedback_count')
    ).outerjoin(Feedback).group_by(Event.id)
    data = [
        dict(
            event_id=e.id,
            title=e.title,
            avg_rating=float(e.avg_rating) if e.avg_rating else 0,
            feedback_count=e.feedback_count
        )
        for e in query.all()
    ]
    return jsonify(data), 200


@app.route('/reports/top-students')
def top_students():
    query = db.session.query(
        Student.id, Student.name,
        func.count(func.distinct(Registration.event_id)).label('total_events'),
        func.count(func.distinct(Attendance.event_id)).label('attended_events')
    ).outerjoin(
        Registration, Student.id == Registration.student_id
    ).outerjoin(
        Attendance, (Attendance.student_id == Student.id) & (Attendance.present == 1)
    ).group_by(Student.id
    ).order_by(func.count(func.distinct(Attendance.event_id)).desc()
    ).limit(3)

    data = [
        dict(
            id=s.id,
            name=s.name,
            total_events=s.total_events or 0,
            attended_events=s.attended_events or 0
        )
        for s in query.all()
    ]
    return jsonify(data), 200


# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(debug=True)
