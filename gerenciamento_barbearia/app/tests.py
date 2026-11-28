from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from app.groups import ADMIN_GROUP, ADMIN_GROUPS, USER_GROUP
from app.models import Service, Visitor


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
    def test_home_shows_login_to_anonymous_users(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Entrar</h1>")

    def test_login_page_uses_base_template(self):
        response = self.client.get("/login/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Entrar</h1>")
        self.assertContains(response, 'href="/static/visitors/css/style.css"')
        self.assertContains(response, 'href="/cadastro/">Cadastrar-se</a>')
        self.assert_guest_client_navigation(response)

    def test_registration_page_shows_public_header_navigation(self):
        response = self.client.get("/cadastro/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/login/">Entrar</a>')
        self.assertContains(response, 'href="/cadastro/">Cadastrar-se</a>')
        self.assert_guest_client_navigation(response)

    def assert_guest_client_navigation(self, response):
        for href, label in (
            ("/dashboard/", "Início"),
            ("/servicos/", "Serviços"),
            ("/agendar/", "Agendar"),
            ("/meus-agendamentos/", "Meus Agendamentos"),
            ("/perfil/", "Perfil"),
            ("/logout/", "Sair"),
        ):
            with self.subTest(label=label):
                self.assertContains(response, f'href="{href}">{label}')

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

    def test_authenticated_client_can_open_booking_page(self):
        user = get_user_model().objects.create_user(
            username="cliente",
            password="senhaSegura123",
        )
        self.client.force_login(user)

        response = self.client.get("/agendar/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Agende seu horário")


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

    def test_client_can_log_in_using_email(self):
        user = get_user_model().objects.create_user(
            username="12345678901",
            email="cliente@example.com",
            password="senhaSegura123",
        )
        user.groups.add(Group.objects.get(name=USER_GROUP))

        response = self.client.post(
            "/login/",
            {"username": "CLIENTE@example.com", "password": "senhaSegura123"},
        )

        self.assertRedirects(response, "/dashboard/", fetch_redirect_response=False)


class RegistrationTests(TestCase):
    def test_client_registration_persists_account_and_visitor_then_redirects_to_login(self):
        response = self.client.post(
            "/cadastro/",
            {
                "cpf": "12345678901",
                "email": "cliente@example.com",
                "password": "Corte!Seguro2026",
                "confirm_password": "Corte!Seguro2026",
            },
        )

        self.assertRedirects(response, "/login/", fetch_redirect_response=False)
        user = get_user_model().objects.get(username="12345678901")
        visitor = Visitor.objects.get(cpf="12345678901")
        self.assertEqual(visitor.user, user)
        self.assertEqual(user.email, "cliente@example.com")
        self.assertTrue(user.groups.filter(name=USER_GROUP).exists())
        self.assertTrue(user.check_password("Corte!Seguro2026"))

        login_response = self.client.post(
            "/login/",
            {"username": "12345678901", "password": "Corte!Seguro2026"},
        )
        self.assertRedirects(
            login_response,
            "/dashboard/",
            fetch_redirect_response=False,
        )

    def test_registration_rejects_an_existing_account_cpf(self):
        get_user_model().objects.create_user(
            username="12345678901",
            password="Corte!Seguro2026",
        )

        response = self.client.post(
            "/cadastro/",
            {
                "cpf": "12345678901",
                "email": "cliente@example.com",
                "password": "Outro!Seguro2026",
                "confirm_password": "Outro!Seguro2026",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Já existe uma conta cadastrada com esse CPF.")
        self.assertEqual(get_user_model().objects.filter(username="12345678901").count(), 1)

    def test_registration_rejects_invalid_cpf_and_duplicate_email(self):
        get_user_model().objects.create_user(
            username="11111111111",
            email="existente@example.com",
            password="SenhaSegura123",
        )

        invalid_cpf_response = self.client.post(
            "/cadastro/",
            {
                "cpf": "123",
                "email": "novo@example.com",
                "password": "Corte!Seguro2026",
                "confirm_password": "Corte!Seguro2026",
            },
        )
        self.assertContains(invalid_cpf_response, "Informe um CPF com 11 números.")

        duplicate_email_response = self.client.post(
            "/cadastro/",
            {
                "cpf": "22222222222",
                "email": "EXISTENTE@example.com",
                "password": "Corte!Seguro2026",
                "confirm_password": "Corte!Seguro2026",
            },
        )
        self.assertContains(
            duplicate_email_response,
            "Já existe uma conta cadastrada com esse e-mail.",
        )


class ProfileValidationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cliente",
            email="cliente@example.com",
            password="senhaSegura123",
        )
        self.client.force_login(self.user)

    def test_profile_update_saves_validated_name_and_email(self):
        response = self.client.post(
            "/perfil/",
            {"first_name": "Lucas", "email": "lucas@example.com"},
        )

        self.assertRedirects(response, "/perfil/", fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Lucas")
        self.assertEqual(self.user.email, "lucas@example.com")

    def test_profile_rejects_email_used_by_another_user(self):
        get_user_model().objects.create_user(
            username="outro",
            email="outro@example.com",
            password="senhaSegura123",
        )

        response = self.client.post(
            "/perfil/",
            {"first_name": "Lucas", "email": "OUTRO@example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este e-mail já está sendo usado por outra conta.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "cliente@example.com")


class ServiceCrudTests(TestCase):
    def setUp(self):
        admin = get_user_model().objects.create_user(
            username="admin",
            password="senhaSegura123",
        )
        admin.groups.add(Group.objects.get(name=ADMIN_GROUP))
        self.client.force_login(admin)

    def test_admin_can_create_read_update_and_delete_service(self):
        create_response = self.client.post(
            "/admin/servicos/",
            {
                "name": "Corte",
                "description": "Corte tradicional",
                "price": "35.00",
                "duration_minutes": "30",
                "active": "on",
            },
        )
        self.assertRedirects(
            create_response,
            "/admin/servicos/",
            fetch_redirect_response=False,
        )
        service = Service.objects.get(name="Corte")

        read_response = self.client.get("/admin/servicos/")
        self.assertContains(read_response, "Corte")

        update_response = self.client.post(
            f"/admin/servicos/{service.pk}/editar/",
            {
                "name": "Corte premium",
                "description": "Corte atualizado",
                "price": "45.00",
                "duration_minutes": "45",
                "active": "on",
            },
        )
        self.assertRedirects(
            update_response,
            "/admin/servicos/",
            fetch_redirect_response=False,
        )
        service.refresh_from_db()
        self.assertEqual(service.name, "Corte premium")
        self.assertEqual(service.price, 45)

        delete_response = self.client.post(
            f"/admin/servicos/{service.pk}/excluir/"
        )
        self.assertRedirects(
            delete_response,
            "/admin/servicos/",
            fetch_redirect_response=False,
        )
        self.assertFalse(Service.objects.filter(pk=service.pk).exists())

    def test_admin_cannot_create_service_with_nonpositive_price_or_duration(self):
        response = self.client.post(
            "/admin/servicos/",
            {
                "name": "Serviço inválido",
                "description": "",
                "price": "0",
                "duration_minutes": "0",
                "active": "on",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "O preço deve ser maior que zero.")
        self.assertContains(response, "A duração deve ser maior que zero.")
        self.assertFalse(Service.objects.exists())


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