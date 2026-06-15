from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date

def check_upcoming_classes(app):
    from models import Schedule, ClassStatus
    with app.app_context():
        now = datetime.now()
        today = date.today()
        day_name = today.strftime('%A')
        classes = Schedule.query.filter_by(day_of_week=day_name).all()
        for cls in classes:
            class_hour, class_min = map(int, cls.class_time.split(':'))
            class_dt = now.replace(hour=class_hour, minute=class_min, second=0, microsecond=0)
            diff = (class_dt - now).total_seconds() / 60
            if 14 <= diff <= 15 or 9 <= diff <= 10 or 4 <= diff <= 5:
                status = ClassStatus.query.filter_by(schedule_id=cls.id, date=today).first()
                if not status:
                    print(f"\n[ALERT] {cls.subject} at {cls.class_time} - Faculty hasn't responded! ({int(diff)} mins left)")

def start_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: check_upcoming_classes(app), trigger='interval', seconds=60)
    scheduler.start()
    return scheduler