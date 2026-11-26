from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        post_migrate.connect(create_user_groups, dispatch_uid='app.create_user_groups')


def create_user_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    from .groups import ADMIN_GROUPS, USER_GROUP

    for group_name in (*ADMIN_GROUPS, USER_GROUP):
        Group.objects.get_or_create(name=group_name)
