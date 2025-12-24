from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Donor, Hospital, BloodRequest, DonationHistory
from datetime import date, timedelta

class BloodBankSystemTest(TestCase):
    def setUp(self):
        """Set up initial data for testing"""
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            username='test@gmail.com', 
            email='test@gmail.com', 
            password='password123',
            first_name='Pratikshya'
        )
        # Create a test hospital
        self.hospital = Hospital.objects.create(
            name="Kathmandu Model Hospital",
            address="Exhibition Road",
            contact_number="014242314",
            license_id="HOSP-999"
        )
        # Create a test donor
        self.donor = Donor.objects.create(
            user=self.user,
            blood_group='O+',
            phone='9841234567',
            address='Kathmandu'
        )

    # --- MODEL TESTS ---

    def test_nepali_phone_validation(self):
        """Ensure only valid Nepali 10-digit numbers starting with 97 or 98 are allowed"""
        # Invalid start digit
        invalid_donor = Donor(user=self.user, blood_group='A+', phone='9612345678', address='KTM')
        with self.assertRaises(ValidationError):
            invalid_donor.full_clean()
        
        # Invalid length
        short_phone = Donor(user=self.user, blood_group='A+', phone='9841', address='KTM')
        with self.assertRaises(ValidationError):
            short_phone.full_clean()

    def test_donor_donation_eligibility(self):
        """Test the 90-day cooldown logic for donors"""
        # Scenario: Last donated 30 days ago (Should be False)
        self.donor.last_donation_date = date.today() - timedelta(days=30)
        self.assertFalse(self.donor.can_donate())
        
        # Scenario: Last donated 95 days ago (Should be True)
        self.donor.last_donation_date = date.today() - timedelta(days=95)
        self.assertTrue(self.donor.can_donate())

    def test_otp_generation_logic(self):
        """Ensure OTP is generated and is exactly 6 digits"""
        otp = self.donor.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())

    # --- VIEW TESTS ---

    def test_login_and_profile_access(self):
        """Check if a logged-in user can access their profile"""
        self.client.login(username='test@gmail.com', password='password123')
        response = self.client.get(reverse('donor_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pratikshya')

    def test_otp_verification_view(self):
        """Test the OTP verification process via POST request"""
        self.client.login(username='test@gmail.com', password='password123')
        otp = self.donor.generate_otp()
        
        # Post the correct OTP
        response = self.client.post(reverse('verify_otp'), {'otp_code': otp})
        
        self.donor.refresh_from_db()
        self.assertTrue(self.donor.is_phone_verified)
        self.assertIsNone(self.donor.otp_code) # Should clear after success
        self.assertRedirects(response, reverse('donor_profile'))

    def test_blood_request_submission(self):
        """Test creating a new blood request through the UI"""
        self.client.login(username='test@gmail.com', password='password123')
        
        payload = {
            'blood_group': 'B-',
            'quantity': 2,
            'hospital': self.hospital.id,
            'required_date': (date.today() + timedelta(days=5)).isoformat()
        }
        response = self.client.post(reverse('donor_request_blood'), payload)
        # response = self.client.post(reverse('request_blood'), payload)
        
        # Check if DB count increased
        self.assertEqual(BloodRequest.objects.count(), 1)
        # Check if the record matches input
        new_request = BloodRequest.objects.first()
        self.assertEqual(new_request.blood_group, 'B-')
        self.assertEqual(new_request.status, 'Pending')

    def test_unauthenticated_access_redirect(self):
        """Ensure profile is protected by @login_required"""
        self.client.logout()
        response = self.client.get(reverse('donor_profile'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/donor/login', response.url)