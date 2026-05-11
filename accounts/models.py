from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    class Role(models.TextChoices):
        MANAGER = 'MANAGER', 'Property Manager'
        STAFF = 'STAFF', 'Maintenance Staff'
        RESIDENT = 'RESIDENT', 'Resident'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.RESIDENT,  
    )

    @property
    def is_manager(self) -> bool:  
        return self.role == self.Role.MANAGER

    @property
    def is_staff_member(self) -> bool:  
        return self.role == self.Role.STAFF
    
    @property
    def is_resident(self) -> bool:  
        return self.role == self.Role.RESIDENT
    
    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
