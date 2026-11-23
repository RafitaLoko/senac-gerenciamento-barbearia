from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from app.groups import ADMIN_GROUP, USER_GROUP


class UserTypesTests(TestCase):
    def test_required_groups_exist(self):
        self.assertTrue(Group.objects.filter(name=ADMIN_GROUP).exists())
        self.assertTrue(Group.objects.filter(name=USER_GROUP).exists())

    def test_users_can_belong_to_each_type(self):
        user = get_user_model().objects.create_user(
            username='testecpf',
            password='senhaSegura123',
        )

        admin = get_user_model().objects.create_user(
            username='admincpf',
            password='senhaSegura123',
        )

        user.groups.add(Group.objects.get(name=USER_GROUP))
        admin.groups.add(Group.objects.get(name=ADMIN_GROUP))

        self.assertTrue(user.groups.filter(name=USER_GROUP).exists())
        self.assertTrue(admin.groups.filter(name=ADMIN_GROUP).exists())