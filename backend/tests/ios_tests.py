import unittest
from flask_testing import TestCase
from datetime import datetime, timedelta
from backend.server import app as flask_app


class TestApp(TestCase):

    def setUp(self):
        self.test_phone_number = "9416616303"

    def create_app(self):
        flask_app.config['TESTING'] = True
        return flask_app

    def test_1_send_message(self):
        response = self.client.post('/send_message', json={
            "phoneNumber": self.test_phone_number,
            "message": "Test message",
            # set scheduled_time to 5 minutes in the future
            "scheduleTime": (datetime.now() + timedelta(minutes=1)).isoformat()
        })

        self.assertEqual(response.status_code, 200)
        print(response.json)  # print the response to debug
        self.assertEqual(response.json["status"], "Message scheduled")
        job_id = response.json["data"]["job_id"]
        self.client.post('/remove_scheduled_message', json={
            "job_id": job_id
        })

    def test_4_remove_scheduled_message(self):
        response = self.client.get('/get_scheduled_messages')
        print(response.json)  # print the response to debug
        job_id = response.json[0]["job_id"]
        response = self.client.post('/remove_scheduled_message', json={
            "job_id": job_id
        })
        print(response.json)  # print the response to debug
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Job removed")

    def test_3_get_scheduled_messages(self):
        response = self.client.get('/get_scheduled_messages')
        print(response.json)  # print the response to debug
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)

    def test_2_modify_scheduled_message(self):
        response = self.client.post('/send_message', json={
            "phoneNumber": self.test_phone_number,
            "message": "Test message",
            "scheduleTime": (datetime.now() + timedelta(minutes=1)).isoformat()
        })
        print(response.json)  # print the response to debug
        job_id = response.json["data"]["job_id"]

        response = self.client.post('/modify_scheduled_message', json={
            "job_id": job_id,
            "new_message": "Modified message"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "Job modified")


if __name__ == '__main__':
    unittest.main()
