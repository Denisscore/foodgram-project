from django.contrib.auth import get_user_model

from django.db import models

User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name="unique_together")
        ]
    def __str__(self):
        return f'{self.user} подписан на {self.author}.'
