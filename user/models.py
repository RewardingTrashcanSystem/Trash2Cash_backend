from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^\+?\d{9,15}$',
    message="Phone number must be in the format +2519XXXXXXXX"
)


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone_number, password=None):
        if not email:
            raise ValueError("Email is required")
        
        if not phone_number:
            raise ValueError("Phone number is required")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, phone_number, password):
        user = self.create_user(email, first_name, last_name, phone_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(
        max_length=15,
        validators=[phone_validator],
        unique=True
    )

    image = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True
    )
    total_points = models.PositiveIntegerField(default=10)
    eco_level = models.CharField(
        max_length=30,
        default="Newbie"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']
    def update_eco_level(self):
        """Update eco level based on total points"""
        if self.total_points >= 1000:
            self.eco_level = "Master Eco"
        elif self.total_points >= 500:
            self.eco_level = "Eco Warrior"
        elif self.total_points >= 200:
            self.eco_level = "Eco Enthusiast"
        elif self.total_points >= 100:
            self.eco_level = "Eco Beginner"
        else:
            self.eco_level = "Newbie"
        self.save(update_fields=["eco_level"])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name