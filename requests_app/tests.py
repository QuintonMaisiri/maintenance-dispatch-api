"""
End-to-end tests that prove the access-control claims in the README.

Run with:  python manage.py test
"""
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import MaintenanceRequest


class AccessControlTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user(
            username='mgr', password='pw12345!', role=User.Role.MANAGER
        )
        cls.staff_a = User.objects.create_user(
            username='sa', password='pw12345!', role=User.Role.STAFF
        )
        cls.staff_b = User.objects.create_user(
            username='sb', password='pw12345!', role=User.Role.STAFF
        )
        cls.res_a = User.objects.create_user(
            username='ra', password='pw12345!', role=User.Role.RESIDENT
        )
        cls.res_b = User.objects.create_user(
            username='rb', password='pw12345!', role=User.Role.RESIDENT
        )

        cls.req_a = MaintenanceRequest.objects.create(
            title='A leaky tap', description='drip', created_by=cls.res_a
        )
        cls.req_b = MaintenanceRequest.objects.create(
            title='B broken light',
            description='out',
            created_by=cls.res_b,
            assigned_to=cls.staff_a,
            status=MaintenanceRequest.Status.IN_PROGRESS,
        )

    # ------------------------------------------------------------------ helpers
    def login(self, user):
        self.client.force_login(user)

    def list_url(self):
        return '/api/requests/'

    def detail_url(self, obj):
        return f'/api/requests/{obj.pk}/'

    # ----------------------------------------------------------------- resident
    def test_resident_sees_only_own_requests(self):
        self.login(self.res_a)
        resp = self.client.get(self.list_url())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = {r['id'] for r in resp.data['results']}
        self.assertEqual(ids, {self.req_a.id})

    def test_resident_cannot_retrieve_other_residents_request(self):
        self.login(self.res_a)
        resp = self.client.get(self.detail_url(self.req_b))
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN,
                                         status.HTTP_404_NOT_FOUND))

    def test_resident_can_create_request(self):
        self.login(self.res_a)
        resp = self.client.post(
            self.list_url(),
            {'title': 'New', 'description': 'thing'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['created_by']['id'], self.res_a.id)
        self.assertEqual(resp.data['status'], 'PENDING')

    def test_resident_cannot_update_request(self):
        self.login(self.res_a)
        resp = self.client.patch(
            self.detail_url(self.req_a),
            {'status': 'COMPLETED'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------------------------------------------------- staff
    def test_staff_sees_only_assigned(self):
        self.login(self.staff_a)
        resp = self.client.get(self.list_url())
        ids = {r['id'] for r in resp.data['results']}
        self.assertEqual(ids, {self.req_b.id})

    def test_staff_cannot_view_request_assigned_to_other_staff(self):
        self.login(self.staff_b)
        resp = self.client.get(self.detail_url(self.req_b))
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN,
                                         status.HTTP_404_NOT_FOUND))

    def test_staff_can_update_status_only(self):
        self.login(self.staff_a)
        # Allowed
        resp = self.client.patch(
            self.detail_url(self.req_b),
            {'status': 'COMPLETED'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'COMPLETED')

        # Not allowed: title change
        resp = self.client.patch(
            self.detail_url(self.req_b),
            {'title': 'hijack'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_cannot_reassign(self):
        self.login(self.staff_a)
        resp = self.client.patch(
            self.detail_url(self.req_b),
            {'assigned_to_id': self.staff_b.id},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_cannot_create(self):
        self.login(self.staff_a)
        resp = self.client.post(
            self.list_url(),
            {'title': 'x', 'description': 'y'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ------------------------------------------------------------------ manager
    def test_manager_sees_all(self):
        self.login(self.manager)
        resp = self.client.get(self.list_url())
        ids = {r['id'] for r in resp.data['results']}
        self.assertEqual(ids, {self.req_a.id, self.req_b.id})

    def test_manager_can_assign(self):
        self.login(self.manager)
        resp = self.client.patch(
            self.detail_url(self.req_a),
            {'assigned_to_id': self.staff_b.id},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['assigned_to']['id'], self.staff_b.id)

    def test_manager_cannot_assign_to_a_resident(self):
        self.login(self.manager)
        resp = self.client.patch(
            self.detail_url(self.req_a),
            {'assigned_to_id': self.res_b.id},
            format='json',
        )
        # PrimaryKeyRelatedField queryset is filtered to STAFF, so this 400s.
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------- unauthenticated
    def test_anonymous_blocked(self):
        resp = self.client.get(self.list_url())
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)