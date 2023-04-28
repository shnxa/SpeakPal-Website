from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            return ValueError('The given email must be set!')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **kwargs)
        user.create_activation_code()
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **kwargs):
        print(email)
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        kwargs.setdefault('is_active', False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)
        return self._create_user(email, password, **kwargs)


class CustomUser(AbstractUser):
    ENGLISH_LEVELS = (
        (1, 'Elementary'), (2, 'Pre-Intermediate'), (3, 'Intermediate'), (4,'Upper-Intermediate'), (5, 'Advanced'),
        (6, 'Proficient'))

    GENDER_CHOICES = (
        (1, 'Male'), (2, 'Female'), (3, 'Prefer not to say')
    )

    email = models.EmailField('email address', unique=True)
    password = models.CharField(max_length=255)
    activation_code = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=70)
    last_name = models.CharField(max_length=70)
    mlang = models.CharField(max_length=70)
    eng_level = models.PositiveSmallIntegerField(choices=ENGLISH_LEVELS)
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES)
    friends = models.ManyToManyField('account.CustomUser', blank=True, related_name='related_friends')


    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.email}'

    def create_activation_code(self):
        import uuid
        code = str(uuid.uuid4())
        self.activation_code = code


class FriendRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='to_user', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{CustomUser.from_user.email}'

    class Meta:
        unique_together = ['from_user', 'to_user']