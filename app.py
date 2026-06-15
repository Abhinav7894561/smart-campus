from flask import Flask, render_template, request, redirect, url_for
from models import db, Schedule, ClassStatus
from datetime import datetime, date
from scheduler import start_scheduler
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/faculty')
def faculty():
    today = date.today()
    day_name = today.strftime('%A')
    classes = Schedule.query.filter_by(day_of_week=day_name).all()
    return render_template('faculty.html', classes=classes, today=today)

@app.route('/student')
def student():
    today = date.today()
    day_name = today.strftime('%A')
    all_classes = Schedule.query.filter_by(day_of_week=day_name).all()
    statuses_dict = {}
    for s in ClassStatus.query.filter_by(date=today).all():
        statuses_dict[s.schedule_id] = s
    class_data = []
    for cls in all_classes:
        status = statuses_dict.get(cls.id)
        class_data.append({
            'subject': cls.subject,
            'class_time': cls.class_time,
            'classroom_no': cls.classroom_no,
            'status': status.status if status else 'pending',
            'substitute_name': status.substitute_name if status else ''
        })
    return render_template('student.html', class_data=class_data, today=today)

@app.route('/hod')
def hod():
    today = date.today()
    day_name = today.strftime('%A')
    all_classes = Schedule.query.filter_by(day_of_week=day_name).all()
    responded = [s.schedule_id for s in ClassStatus.query.filter_by(date=today).all()]
    no_response = [c for c in all_classes if c.id not in responded]
    return render_template('hod.html', no_response=no_response, today=today)

@app.route('/respond/<int:schedule_id>', methods=['POST'])
def respond(schedule_id):
    status = request.form.get('status')
    substitute_name = request.form.get('substitute_name', '')
    today = date.today()
    existing = ClassStatus.query.filter_by(schedule_id=schedule_id, date=today).first()
    if existing:
        existing.status = status
        existing.substitute_name = substitute_name
        existing.updated_at = datetime.now()
    else:
        new_status = ClassStatus(
            schedule_id=schedule_id,
            date=today,
            status=status,
            substitute_name=substitute_name
        )
        db.session.add(new_status)
    db.session.commit()
    return redirect(url_for('faculty'))

@app.route('/timetable')
def timetable():
    classes = Schedule.query.all()
    return render_template('timetable.html', classes=classes)

@app.route('/timetable/add', methods=['POST'])
def add_class():
    subject = request.form.get('subject')
    faculty_name = request.form.get('faculty_name')
    class_time = request.form.get('class_time')
    day_of_week = request.form.get('day_of_week')
    classroom_no = request.form.get('classroom_no')
    new_class = Schedule(subject=subject, faculty_name=faculty_name, class_time=class_time, day_of_week=day_of_week, classroom_no=classroom_no)
    db.session.add(new_class)
    db.session.commit()
    return redirect(url_for('timetable'))

@app.route('/timetable/delete/<int:schedule_id>')
def delete_class(schedule_id):
    cls = Schedule.query.get(schedule_id)
    if cls:
        db.session.delete(cls)
        db.session.commit()
    return redirect(url_for('timetable'))

@app.route('/preconfirm')
def preconfirm():
    from datetime import timedelta
    tomorrow = date.today() + timedelta(days=1)
    day_name = tomorrow.strftime('%A')
    classes = Schedule.query.filter_by(day_of_week=day_name).all()
    return render_template('preconfirm.html', classes=classes, tomorrow=tomorrow)

@app.route('/preconfirm/submit', methods=['POST'])
def preconfirm_submit():
    from datetime import timedelta
    tomorrow = date.today() + timedelta(days=1)
    schedule_ids = request.form.getlist('schedule_ids')
    for sid in schedule_ids:
        existing = ClassStatus.query.filter_by(schedule_id=int(sid), date=tomorrow).first()
        if existing:
            existing.status = 'happening'
            existing.updated_at = datetime.now()
        else:
            new_status = ClassStatus(
                schedule_id=int(sid),
                date=tomorrow,
                status='happening'
            )
            db.session.add(new_status)
    db.session.commit()
    return redirect(url_for('preconfirm') + '?confirmed=1')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        start_scheduler(app)
    app.run(debug=True, host='0.0.0.0')