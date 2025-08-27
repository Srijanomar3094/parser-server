from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Contract
import json


class ContractModelTest(TestCase):
    def setUp(self):
        self.contract = Contract.objects.create(
            original_filename="test_contract.pdf",
            status=Contract.STATUS_PENDING
        )

    def test_contract_creation(self):
        self.assertEqual(self.contract.original_filename, "test_contract.pdf")
        self.assertEqual(self.contract.status, Contract.STATUS_PENDING)
        self.assertEqual(self.contract.progress, 0)
        self.assertEqual(self.contract.score, 0)

    def test_contract_string_representation(self):
        expected = f"Contract #{self.contract.pk} - test_contract.pdf"
        self.assertEqual(str(self.contract), expected)


class ContractAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('contract_upload')
        self.test_pdf_content = b'%PDF-1.4\n%Test PDF content'

    def test_contract_upload_success(self):
        file_data = SimpleUploadedFile(
            "test_contract.pdf",
            self.test_pdf_content,
            content_type="application/pdf"
        )
        
        response = self.client.post(self.upload_url, {'file': file_data})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('contract_id', data)
        
        # Check if contract was created
        contract = Contract.objects.get(pk=data['contract_id'])
        self.assertEqual(contract.original_filename, "test_contract.pdf")
        self.assertEqual(contract.status, Contract.STATUS_PENDING)

    def test_contract_upload_no_file(self):
        response = self.client.post(self.upload_url, {})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('detail', data)

    def test_contract_upload_wrong_file_type(self):
        file_data = SimpleUploadedFile(
            "test.txt",
            b"Not a PDF file",
            content_type="text/plain"
        )
        
        response = self.client.post(self.upload_url, {'file': file_data})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('detail', data)

    def test_contract_status(self):
        contract = Contract.objects.create(
            original_filename="test.pdf",
            status=Contract.STATUS_COMPLETED,
            progress=100
        )
        
        status_url = reverse('contract_status', args=[contract.pk])
        response = self.client.get(status_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], Contract.STATUS_COMPLETED)
        self.assertEqual(data['progress'], 100)

    def test_contract_detail(self):
        contract = Contract.objects.create(
            original_filename="test.pdf",
            status=Contract.STATUS_COMPLETED,
            progress=100,
            score=85
        )
        
        detail_url = reverse('contract_detail', args=[contract.pk])
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['score'], 85)
        self.assertEqual(data['status'], Contract.STATUS_COMPLETED)

    def test_contract_list(self):
        # Create multiple contracts
        Contract.objects.create(
            original_filename="contract1.pdf",
            status=Contract.STATUS_COMPLETED,
            score=90
        )
        Contract.objects.create(
            original_filename="contract2.pdf",
            status=Contract.STATUS_PENDING
        )
        
        list_url = reverse('contract_list')
        response = self.client.get(list_url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['count'], 2)

    def test_contract_list_filtering(self):
        Contract.objects.create(
            original_filename="completed.pdf",
            status=Contract.STATUS_COMPLETED
        )
        Contract.objects.create(
            original_filename="pending.pdf",
            status=Contract.STATUS_PENDING
        )
        
        list_url = reverse('contract_list')
        response = self.client.get(f"{list_url}?status=completed")
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['status'], Contract.STATUS_COMPLETED)


class ContractScoringTest(TestCase):
    def test_scoring_algorithm(self):
        contract = Contract.objects.create(
            original_filename="test.pdf",
            status=Contract.STATUS_PENDING
        )
        
        # Test with complete data
        contract.parties = {
            "customer": "Test Customer",
            "vendor": "Test Vendor",
            "signatories": ["John Doe"]
        }
        contract.financial_details = {
            "line_items": [{"item": "Service", "price": 100}],
            "total_value": 100,
            "currency": "USD",
            "taxes": 10
        }
        contract.payment_structure = {
            "terms": "Net 30",
            "schedule": "Monthly",
            "method": "Bank Transfer",
            "banking": {"account": "123456"}
        }
        contract.sla = {
            "metrics": "99.9% uptime",
            "penalties": "Service credits",
            "support": "24/7 support"
        }
        contract.account_info = {
            "billing_contact": "billing@test.com",
            "technical_contact": "tech@test.com"
        }
        
        # This would normally be called by the parsing function
        # For testing, we'll call it directly
        from .views import _score_and_gaps
        _score_and_gaps(contract)
        
        # Should get full score (100 points)
        self.assertEqual(contract.score, 100)
        self.assertEqual(len(contract.gaps), 0)

