from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Review(models.Model):
    reviewed_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_review')
    reviewer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reviewer')
    review = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user} - {self.review}'