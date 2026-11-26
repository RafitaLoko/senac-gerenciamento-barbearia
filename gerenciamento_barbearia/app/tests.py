from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from app.groups import ADMIN_GROUP, ADMIN_GROUPS, USER_GROUP


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


class DashboardTests(TestCase):
    def test_home_redirects_anonymous_users_to_login(self):
        response = self.client.get("/", follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=/")

    def test_login_page_uses_base_template(self):
        response = self.client.get("/login/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Entrar</h1>")
        self.assertContains(response, 'href="/static/visitors/css/style.css"')

    def test_authenticated_user_can_open_dashboard(self):
        user = get_user_model().objects.create_user(
            username="cliente",
            password="senhaSegura123",
        )
        self.client.force_login(user)

        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bem-vindo, cliente!")
        self.assertContains(response, 'href="/static/visitors/css/style.css"')


class RoleLoginTests(TestCase):
    def test_client_login_redirects_to_dashboard(self):
        user = get_user_model().objects.create_user(
            username="clientecpf",
            password="senhaSegura123",
        )
        user.groups.add(Group.objects.get(name=USER_GROUP))

        response = self.client.post(
            "/login/",
            {"username": "clientecpf", "password": "senhaSegura123"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/dashboard/")

    def test_admin_login_redirects_to_admin_panel(self):
        admin = get_user_model().objects.create_user(
            username="admincpf",
            password="senhaSegura123",
        )
        admin.groups.add(Group.objects.get(name=ADMIN_GROUP))

        response = self.client.post(
            "/login/",
            {"username": "admincpf", "password": "senhaSegura123"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin-painel/")


class AdminPanelTests(TestCase):
    def test_admin_group_names_can_open_admin_panel(self):
        for index, group_name in enumerate(ADMIN_GROUPS):
            with self.subTest(group_name=group_name):
                admin = get_user_model().objects.create_user(
                    username=f"admin{index}",
                    password="senhaSegura123",
                )
                admin.groups.add(Group.objects.get(name=group_name))
                self.client.force_login(admin)

                response = self.client.get("/admin-painel/")

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'class="visitor-table"')

    def test_admin_panel_remains_restricted_to_admin_groups(self):
        user = get_user_model().objects.create_user(
            username="cliente",
            password="senhaSegura123",
        )
        user.groups.add(Group.objects.get(name=USER_GROUP))
        self.client.force_login(user)

        response = self.client.get("/admin-painel/")

        self.assertEqual(response.status_code, 403)