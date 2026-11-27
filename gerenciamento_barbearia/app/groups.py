ADMIN_GROUP = 'Administrador'
ADMIN_GROUPS = (ADMIN_GROUP, 'admin')
USER_GROUP = 'Usuário'

# Compatibilidade temporária com referências antigas.
VISITOR_GROUP = USER_GROUP


def is_admin_user(user):
    return bool(
        user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or user.groups.filter(name__in=ADMIN_GROUPS).exists()
        )
    )
