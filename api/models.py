from django.contrib.auth.models import User
from django.db import models
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending')

    def save(self, *args, **kwargs):
        now = timezone.now()
        cache_key = f'friend_requests_{self.from_user.id}'
        recent_requests = cache.get(cache_key, [])
        if recent_requests:
            recent_requests = [req for req in recent_requests if req > now - timedelta(minutes=1)]
            if len(recent_requests) >= 3:
                raise Exception("Rate limit exceeded")
        else:
            recent_requests = []
        recent_requests.append(now)
        cache.set(cache_key, recent_requests, timeout=60)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ['from_user', 'to_user']
