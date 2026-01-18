"""Tests for medicheck ApIs"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Disease,
    Tag,
)


from medicheck.serializers import (
    DiseaseSerializer,
    DiseaseDetailSerializer,
)

DISEASES_URL = reverse('medicheck:disease-list')

def detail_url(disease_id):
    """Create and return a disease detail URL."""
    return reverse('medicheck:disease-detail', args=[disease_id])


def create_disease(user, **params):
    defaults = {
        'name': 'Malaria',
        'description': 'Caused by mosquito bites',
        'cause': 'Plasmodium parasite',
        'symptoms': 'Fever, chills, headache',
        'prevention': 'Mosquito nets, repellents',
        'link': 'https://example.com/malaria-info',
    }
    defaults.update(params)
    return Disease.objects.create(user=user, **defaults)


def create_user(**params):
    """Create and return a user"""
    return get_user_model().objects.create_user(**params)



class PublicDiseaseApiTests(TestCase):
    """Test the public  unauthenticated API for diseases"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required to call the API"""
        res = self.client.get(DISEASES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDiseaseApiTests(TestCase):
    """Test the authenticated API for diseases request"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password= 'test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_diseases(self):
        """Test retrieving a list of diseases"""
        create_disease(user=self.user)
        create_disease(user=self.user)

        res = self.client.get(DISEASES_URL)

        diseases = Disease.objects.all().order_by('id')
        serializer = DiseaseSerializer(diseases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_disease_list_limited_to_user(self):
        """Test that the disease list is limited to the authenticated user"""
        other_user = create_user(email='other@example.com', password='test123',)
        create_disease(user=other_user)
        create_disease(user=self.user)

        res = self.client.get(DISEASES_URL)
        diseases = Disease.objects.filter(user=self.user)
        serializer = DiseaseSerializer(diseases, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_disease_detail(self):
        """Test get recipe detail."""
        disease = create_disease(user=self.user)

        url = detail_url(disease.id)
        res = self.client.get(url)

        serializer = DiseaseDetailSerializer(disease)
        self.assertEqual(res.data, serializer.data)

    def test_create_disease(self):
        """Test creating a disease"""
        payload = {
            'name': 'Malaria',
            'description': 'A disease caused by Plasmodium parasite.',
            'symptoms': 'Fever, chills, headache',
            'cause': 'Mosquito bite',
            'prevention': 'Use mosquito nets',
        }
        res = self.client.post(DISEASES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        disease = Disease.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(disease, k), v)
        self.assertEqual(disease.user, self.user)


    def test_partial_update(self):
        """Test partial update of a disease"""
        original_link= 'https://example.com/disease.pdf'
        disease = create_disease(
            user=self.user,
            name='Sample disease name',
            link = original_link,

        )

        payload = {'name': 'New disease title'}
        url = detail_url(disease.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        disease.refresh_from_db()
        self.assertEqual(disease.name, payload['name'])
        self.assertEqual(disease.link, original_link)
        self.assertEqual(disease.user, self.user)

    def test_full_update(self):
        """Test full update of recipe."""
        disease = create_disease(
            user=self.user,
            name = 'Sample disease name',
            link='https://example.com/disease.pdf',
            description='Sample disease description',
        )

        payload = {
            'name': 'Malaria',
            'description': 'A disease caused by Plasmodium parasite.',
            'symptoms': 'Fever, chills, headache',
            'cause': 'Mosquito bite',
            'prevention': 'Use mosquito nets',
        }
        url = detail_url(disease.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        disease.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(disease, k), v)
        self.assertEqual(disease.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the disease user results in an error."""
        new_user = create_user(email='user2example.com', password='test123')
        disease = create_disease(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(disease.id)
        self.client.patch(url, payload)

        disease.refresh_from_db()
        self.assertEqual(disease.user, self.user)

    def test_delete_disease(self):
        """Test deleting disease was successful"""
        disease = create_disease(user=self.user)

        url = detail_url(disease.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Disease.objects.filter(id=disease.id).exists())

    def test_disease_other_users_error(self):
        """Test trying to delete another users disease give error."""
        new_user = create_user(email='user2@example.com', password='test123')
        disease = create_disease(user=new_user)

        url = detail_url(disease.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Disease.objects.filter(id=disease.id).exists())

    def test_create_disease_with_new_tags(self):
        """Test creating a disease with new tags."""
        payload = {
            'name': 'Flu catarrh cold',         # Correct field 'title' to 'name'
            'description': 'Some description',
            'cause': 'Viral infection',
            'prevention': 'Rest and fluids',
            #'symptoms': [{'name': 'Flu'}, {'name': 'Influenza'}],
            'tags': [{'name': 'Viral'}, {'name': 'Influenza'}],        # optional
        }

        res = self.client.post(DISEASES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        diseases = Disease.objects.filter(user=self.user)
        self.assertEqual(diseases.count(), 1)
        disease = diseases[0]
        self.assertEqual(disease.tags.count(), 2)
        for tag in payload['tags']:
            exists = disease.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)


    def test_create_disease_with_existing_tag(self):
        """Test creating a disease with existing tag."""
        tag_indoor = Tag.objects.create(user=self.user, name='Indoor')
        payload = {
            'name': 'Chickenpox',
            'description': 'A contagious disease',
            'cause': 'Varicella-zoster virus',
            'symptoms': 'Itchy rash, fever',
            'prevention': 'Vaccination',
            'tags': [{'name': 'Indoor'}, {'name': 'Viral'}],
        }
        res = self.client.post(DISEASES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        diseases = Disease.objects.filter(user=self.user)
        self.assertEqual(diseases.count(), 1)
        disease = diseases[0]
        self.assertEqual(disease.tags.count(), 2)
        self.assertIn(tag_indoor, disease.tags.all())
        for tag in payload['tags']:
            exists = disease.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a tag when updating a disease."""
        disease = create_disease(user=self.user)

        payload = {'tags': [{'name': 'Chronic'}]}
        url = detail_url(disease.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Chronic')
        self.assertIn(new_tag, disease.tags.all())

    def test_update_disease_assign_tag(self):
        """Test assigning an existing tag when updating a disease."""
        tag_healthy = Tag.objects.create(user=self.user, name='Healthy')
        disease = create_disease(user=self.user)

        disease.tags.add(tag_healthy)

        tag_strict = Tag.objects.create(user=self.user, name='Strict')
        payload = {'tags': [{'name': 'Strict'}]}
        url = detail_url(disease.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_strict, disease.tags.all())
        self.assertNotIn(tag_healthy, disease.tags.all())

    def test_clear_disease_tags(self):
        """Test clearing a disease tags."""
        tag = Tag.objects.create(user=self.user, name='To be cleared')
        disease = create_disease(user=self.user)
        disease.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(disease.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(disease.tags.count(), 0)