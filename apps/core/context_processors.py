import os
from django.conf import settings
from apps.core.models import Notification

def notifications(request):
    """
    Context processor to provide unread notifications count globally.
    """
    pics_dir = settings.BASE_DIR / 'pics'
    motivation_images = []
    if pics_dir.exists():
        for f in os.listdir(pics_dir):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                motivation_images.append(f)

    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0, 'latest_notifications': [], 'motivation_images': motivation_images}

    try:
        notifs = Notification.objects.filter(user=request.user)
        count = notifs.filter(is_read=False).count()
        latest = notifs.order_by('-created_at')[:5]
    except Exception:
        count = 0
        latest = []

    return {
        'unread_notifications_count': count,
        'latest_notifications': latest,
        'motivation_images': motivation_images
    }
