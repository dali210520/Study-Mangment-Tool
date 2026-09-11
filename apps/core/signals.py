from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
import random
from apps.tasks.models import Task
from apps.deadlines.models import Deadline
from apps.core.models import Notification
from apps.courses.models import StudyModule, Lecture
from apps.plans.models import StudyPlanEntry
from apps.materials.models import StudyMaterial

MOTIVATIONS = [
    "🎉 Super gemacht! '{title}' ist erledigt!",
    "🔥 Stark! Wieder eine Aufgabe weniger: '{title}'",
    "✅ Weiter so! Du hast '{title}' abgeschlossen!",
    "🚀 Klasse! '{title}' abgehakt!"
]

@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    link = reverse('ui-task-list')
    if created:
        Notification.objects.create(
            user=instance.user,
            message=f"📝 Neue Aufgabe: {instance.title}",
            link=link
        )
    elif instance.status == Task.Status.DONE:
        # Avoid creating duplicates if saved multiple times
        msg = random.choice(MOTIVATIONS).format(title=instance.title)
        # Check if we already sent a completion notification for THIS task
        from django.db.models import Q
        if not Notification.objects.filter(
            user=instance.user, 
            link=link, 
            message__contains=instance.title
        ).filter(
            Q(message__contains="erledigt") | 
            Q(message__contains="abgeschlossen") | 
            Q(message__contains="abgehakt") | 
            Q(message__contains="weniger")
        ).exists():
            Notification.objects.create(
                user=instance.user,
                message=msg,
                link=link
            )

@receiver(post_save, sender=Deadline)
def create_deadline_notification(sender, instance, created, **kwargs):
    if created:
        link = reverse('ui-deadline-list')
        Notification.objects.create(
            user=instance.user,
            message=f"📅 Neuer Termin: {instance.title}",
            link=link
        )
    elif instance.status == Deadline.Status.COMPLETED:
        link = reverse('ui-deadline-list')
        msg = random.choice(MOTIVATIONS).format(title=instance.title)
        from django.db.models import Q
        if not Notification.objects.filter(
            user=instance.user, 
            link=link, 
            message__contains=instance.title
        ).filter(
            Q(message__contains="erledigt") | 
            Q(message__contains="abgeschlossen") | 
            Q(message__contains="abgehakt") | 
            Q(message__contains="weniger")
        ).exists():
            Notification.objects.create(
                user=instance.user,
                message=msg,
                link=link
            )

@receiver(post_save, sender=StudyModule)
def create_module_notification(sender, instance, created, **kwargs):
    if created:
        link = reverse('ui-module-list')
        Notification.objects.create(
            user=instance.user,
            message=f"📚 Neues Modul: {instance.name}",
            link=link
        )

@receiver(post_save, sender=StudyPlanEntry)
def create_plan_notification(sender, instance, created, **kwargs):
    if created:
        link = reverse('ui-plan-list')
        Notification.objects.create(
            user=instance.user,
            message=f"🗓️ Neuer Lernplan: {instance.topic}",
            link=link
        )
    elif instance.status == StudyPlanEntry.Status.DONE:
        link = reverse('ui-plan-list')
        msg = random.choice(MOTIVATIONS).format(title=instance.topic)
        from django.db.models import Q
        if not Notification.objects.filter(
            user=instance.user, 
            link=link, 
            message__contains=instance.topic
        ).filter(
            Q(message__contains="erledigt") | 
            Q(message__contains="abgeschlossen") | 
            Q(message__contains="abgehakt") | 
            Q(message__contains="weniger")
        ).exists():
            Notification.objects.create(
                user=instance.user,
                message=msg,
                link=link
            )

@receiver(post_save, sender=StudyMaterial)
def create_material_notification(sender, instance, created, **kwargs):
    if created:
        link = reverse('ui-material-list')
        Notification.objects.create(
            user=instance.user,
            message=f"📎 Neues Material: {instance.title}",
            link=link
        )

@receiver(post_save, sender=Lecture)
def create_lecture_notification(sender, instance, created, **kwargs):
    if created:
        link = reverse('ui-lecture-list')
        Notification.objects.create(
            user=instance.module.user,
            message=f"🏫 Neue Vorlesung: {instance.title}",
            link=link
        )
