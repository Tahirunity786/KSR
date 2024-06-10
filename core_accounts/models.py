from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils.text import slugify
import uuid



# Custom user manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    GENDER = (
        ("Male", "Male"),
        ("Female", "Female"),
        ("Not confirmed", "Not confirmed"),
    )
    USER_TYPE_CHOICES = (
        ("tutor", "Tutor"),
        ("tutee", "Tutee"),
    )
    # General Information about the user
    profile = models.ImageField(upload_to="profile/images", blank=True, null=True)
    profile_slug = models.SlugField(unique=True, max_length=255, default='')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    email = models.EmailField(null=False, unique=True)
    date_of_birth = models.DateField(default=None, null=True)
    gender = models.CharField(max_length=100, choices=GENDER, null=True, db_index=True)
    mobile_number = models.BigIntegerField(null=True)
    otp = models.PositiveIntegerField(null=True)
    otp_limit = models.IntegerField(null=True)
    otp_delay = models.TimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=None, null=True)
    is_blocked = models.BooleanField(default=False, null=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user_type = models.CharField(max_length=5, choices=USER_TYPE_CHOICES, default='tutee')

    # Tutor
    hourly_rate = models.IntegerField(db_index=True, null=True)
    response_time = models.CharField(max_length=50, db_index=True, default=None, null=True)
    t_to_number_of_students = models.CharField(max_length=50, db_index=True, default=None, null=True)
    experience = models.TextField(default=None, null=True)

    # Tutee
    info = models.TextField(default=None, null=True)
    degree = models.FileField(upload_to='degrees', db_index=True, null=True, default=None)

    # Global Identity
    reviews = models.ManyToManyField('Reviews', db_index=True)

    password = models.CharField(max_length=200, db_index=True, default=None)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    groups = models.ManyToManyField(Group, related_name='user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions', blank=True)

    def save(self, *args, **kwargs):
        if not self.profile_slug:
            max_slug_length = 255
            username_slug = slugify(self.username)
            uuid_suffix = uuid.uuid4().hex[:8]
            allowed_username_length = max_slug_length - len(uuid_suffix) - 1
            if len(username_slug) > allowed_username_length:
                username_slug = username_slug[:allowed_username_length]
            self.profile_slug = f"{username_slug}-{uuid_suffix}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Reviews(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewer")
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor")
    rating = models.DecimalField(decimal_places=1, max_digits=3)
    reviewer_msg = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
