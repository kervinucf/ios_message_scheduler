from dateutil.parser import parse
from backend.ios.utils import send_ios_message
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from flask_cors import CORS
import subprocess
from datetime import datetime, timedelta


# Helper function to wake up the system at a specified time
def set_wakeup_time(wakeup_time):
    wakeup_time_str = wakeup_time.strftime("%m/%d/%y %H:%M:%S")
    subprocess.run(["pmset", "schedule", "wakeorpoweron", wakeup_time_str])


# Helper function to check if the system is likely in sleep mode
def is_system_in_sleep_mode():
    result = subprocess.run(["ioreg", "-c", "IOHIDSystem"], capture_output=True, text=True)
    lines = result.stdout.split("\n")
    for line in lines:
        if "HIDIdleTime" in line:
            idle_time_ms = int(line.split("=")[-1].strip())
            idle_time_s = idle_time_ms / 1000
            if idle_time_s > 3600:  # if idle for more than 1 hour, consider it in sleep mode
                return True
    return False


app = Flask(__name__)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
        "allow_headers": [
            "Content-Type",
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Methods",
        ]
    }
})
scheduler = BackgroundScheduler()
scheduler.start()


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()

    if 'phoneNumber' not in data or 'message' not in data:
        return {
            "status": "Message not sent. Missing phoneNumber or message field",
        }

    phone_number = data['phoneNumber']
    message = data['message']

    scheduled_time = data.get('scheduleTime')  # Use .get() instead of direct access
    print(f"scheduleTime: {scheduled_time}")

    if scheduled_time:  # If scheduleTime is present, try to schedule the message
        try:
            scheduled_time = parse(scheduled_time)  # Convert from string to datetime

            # Check if the system is likely in sleep mode and if so, set a wake up time
            if is_system_in_sleep_mode():
                # Wake up the system 5 minutes before the message is scheduled to be sent
                wakeup_time = scheduled_time - timedelta(minutes=5)
                set_wakeup_time(wakeup_time)

            trigger = DateTrigger(run_date=scheduled_time)
            job = scheduler.add_job(send_ios_message, trigger, args=[phone_number, message], id=phone_number + message)

            return {
                "status": "Message scheduled",
                "data": {
                    "phoneNumber": phone_number,
                    "message": message,
                    "scheduleTime": scheduled_time,
                    "job_id": job.id
                }
            }
        except Exception as e:
            print(f"Error scheduling message: {e}")
            # Fall through to sending message immediately

    # If scheduleTime is not present, or if scheduling fails, send the message immediately
    send_ios_message(phone_number, message)
    return {
        "status": "Message sent",
    }


@app.route('/get_scheduled_messages', methods=['GET'])
def get_scheduled_messages():
    jobs = scheduler.get_jobs()
    result = [
        {'job_id': job.id, 'next_run_time': job.next_run_time, 'phone_number': job.args[0], 'message': job.args[1]} for
        job in jobs]
    return jsonify(result)


@app.route('/modify_scheduled_message', methods=['POST'])
def modify_scheduled_message():
    data = request.get_json()

    job_id = data.get('job_id')
    new_time = data.get('new_time')
    new_message = data.get('new_message')

    job = scheduler.get_job(job_id)

    if not job:
        return jsonify({'error': 'No such job'})

    if new_time:
        trigger = DateTrigger(run_date=new_time)
        job.modify(trigger=trigger)

    if new_message:
        job.modify(args=[job.args[0], new_message])

    return jsonify({'status': 'Job modified'})


@app.route('/remove_scheduled_message', methods=['POST'])
def remove_scheduled_message():
    data = request.get_json()
    job_id = data.get('job_id')
    job = scheduler.get_job(job_id)

    if not job:
        return jsonify({'error': 'No such job'})

    job.remove()

    return jsonify({'status': 'Job removed'})


if __name__ == '__main__':
    app.run(debug=True)
