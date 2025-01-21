from django.test import TestCase
from .models import Doctor
from hospital.models import Hospital, Department
from utils.logger import Level, log
from django.contrib.auth.models import User, Group, Permission

class DoctorModelTest(TestCase):
    def setUp(self):
        self.hospital = Hospital.objects.create(name="Test Hospital")
        self.department = Department.objects.create(name="Test Department")
        self.doctor = Doctor.objects.create(
            name="Dr. Test",
            hospital=self.hospital,
            department=self.department,
            active=True
        )

    def test_doctor_creation(self):
        self.assertEqual(self.doctor.name, "Dr. Test")
        self.assertEqual(self.doctor.hospital, self.hospital)
        self.assertEqual(self.doctor.department, self.department)
        self.assertTrue(self.doctor.active)

    def test_doctor_str_method(self):
        self.assertEqual(str(self.doctor), "Dr. Test")

    def test_doctor_fields(self):
        # Test that fields are of correct type
        self.assertIsInstance(self.doctor.id, int)
        self.assertIsInstance(self.doctor.name, str)
        self.assertIsInstance(self.doctor.active, bool)
        self.assertIsInstance(self.doctor.hospital, Hospital)
        self.assertIsInstance(self.doctor.department, Department)

    def test_doctor_field_lengths(self):
        # Test max_length of name field
        max_length = self.doctor._meta.get_field('name').max_length
        self.assertEqual(max_length, 128)

    def test_doctor_defaults(self):
        # Test default value of active field
        new_doctor = Doctor.objects.create(
            name="Dr. Default",
            hospital=self.hospital,
            department=self.department
        )
        self.assertTrue(new_doctor.active)

from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from hospital.models import HospitalDepartment
import json

class DoctorViewTests(TestCase):
    def setUp(self):
        self.hospital = Hospital.objects.create(name="Test Hospital")
        self.department = Department.objects.create(name="Test Department")
        # Create valid hospital-department link
        HospitalDepartment.objects.create(hospital=self.hospital, department=self.department)
        
        self.doctor = Doctor.objects.create(
            name="Dr. Test",
            hospital=self.hospital,
            department=self.department
        )
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user.user_permissions.add(
            Permission.objects.get(codename='view_doctor'),
            Permission.objects.get(codename='change_doctor'),
            Permission.objects.get(codename='delete_doctor')
        )
        self.client.login(username='testuser', password='testpass')

    def test_get_doctor_list(self):
        response = self.client.get('/doctors')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], 'Dr. Test')

    def test_create_doctor(self):
        data = {
            'name': 'Dr. New',
            'hospital': 'Test Hospital',
            'department': 'Test Department'
        }
        response = self.client.post('/doctors', data=json.dumps(data), content_type='application/json')
        print("debug message: ", response.json())
        self.assertEqual(response.status_code, 202)
        self.assertEqual(Doctor.objects.count(), 2)
        self.assertEqual(response.json()['name'], 'Dr. New')

    def test_get_single_doctor(self):
        response = self.client.get(f'/doctor/{self.doctor.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Dr. Test')

    def test_update_doctor(self):
        data = {
            'name': 'Dr. Updated',
            'hospital': 'Test Hospital',
            'department': 'Test Department'
        }
        response = self.client.put(
            f'/doctor/{self.doctor.id}',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Dr. Updated')

    def test_delete_doctor(self):
        response = self.client.delete(f'/doctor/{self.doctor.id}')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Doctor.objects.count(), 0)

    def test_invalid_hospital_department_pair(self):
        log(Level.DEBUG, "test_invalid_hospital_department_pair_with_render")
        data = {
            'name': 'Dr. Invalid',
            'hospital': 'Nonexistent Hospital',
            'department': 'Test Department'
        }

        response = self.client.post('/doctors', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_missing_required_fields_json_response(self):
        """Test that KeyError from missing fields is properly JSON serialized in response"""  
        # The view returns the KeyError directly which isn't JSON serializable
        # It should return a dict with an error message instead
        data = {'invalid': 'data'}
        response = self.client.post('/doctors', data=json.dumps(data), content_type='application/json')
        response.render()
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.json(), dict)

class DoctorAuthenticationAuthorizationTests(TestCase):
    def setUp(self):
        self.hospital = Hospital.objects.create(name="Test Hospital")
        self.department = Department.objects.create(name="Test Department")
        self.doctor = Doctor.objects.create(
            name="Dr. Test",
            hospital=self.hospital,
            department=self.department
        )
        self.client = Client()
        self.base_data = {
            'name': 'Dr. New',
            'hospital': 'Test Hospital',
            'department': 'Test Department'
        }

    def test_unauthorized_access(self):
        # Create new user without permissions
        user = User.objects.create_user(username='noauth', password='noauth')
        self.client.login(username='noauth', password='noauth')
        
        # Test all CRUD operations without permissions
        response = self.client.get('/doctors')
        self.assertEqual(response.status_code, 403)
        
        response = self.client.post('/doctors', data=json.dumps(self.base_data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get(f'/doctor/{self.doctor.id}')
        self.assertEqual(response.status_code, 403)
        
        response = self.client.put(f'/doctor/{self.doctor.id}', data=json.dumps(self.base_data), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        
        response = self.client.delete(f'/doctor/{self.doctor.id}')
        self.assertEqual(response.status_code, 403)

