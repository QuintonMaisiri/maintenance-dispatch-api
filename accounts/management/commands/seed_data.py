"""
Create demo users and a couple of maintenance requests.
    python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from requests_app.models import MaintenanceRequest


DEMO_USERS = [
    ('manager',   'manager123',  User.Role.MANAGER,  'manager@example.com'),
    ('staff1',    'staff12345',  User.Role.STAFF,    'staff1@example.com'),
    ('staff2',    'staff12345',  User.Role.STAFF,    'staff2@example.com'),
    ('resident',  'resident123', User.Role.RESIDENT, 'resident@example.com'),
    ('resident2', 'resident123', User.Role.RESIDENT, 'resident2@example.com'),
]


class Command(BaseCommand):
    help = 'Seed demo users and maintenance requests.'

    @transaction.atomic
    def handle(self, *args, **options):
        for username, password, role, email in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'role': role},
            )
            user.role = role
            user.email = email
            user.set_password(password)
            # Give the manager Django admin access too, so reviewers can
            # inspect the database via /admin/ without shell access.
            if role == User.Role.MANAGER:
                user.is_staff = True
                user.is_superuser = True
            user.save()
            verb = 'Created' if created else 'Updated'
            self.stdout.write(f'{verb} {role:<8} -> {username} / {password}')

        resident = User.objects.get(username='resident')
        staff1 = User.objects.get(username='staff1')

        if MaintenanceRequest.objects.count() == 0:
            MaintenanceRequest.objects.create(
                title='Leaky kitchen tap',
                description='The cold-water tap drips constantly.',
                created_by=resident,
            )
            MaintenanceRequest.objects.create(
                title='Broken hallway light',
                description='Bulb out on the second floor landing.',
                created_by=resident,
                assigned_to=staff1,
                status=MaintenanceRequest.Status.IN_PROGRESS,
            )
            self.stdout.write('Created sample maintenance requests.')

        self.stdout.write(self.style.SUCCESS('Seed complete.'))