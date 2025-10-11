from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver


class ConstantGroups:
    """Constants for group names"""
    ADMIN = "Admin"
    SUPERVISOR = "Supervisor"
    WORKER = "Worker"

    ALL_GROUPS = [ADMIN, SUPERVISOR, WORKER]


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """Create constant groups after migrations"""
    groups_permissions = {
        ConstantGroups.ADMIN: [
            "add_activitystatistics",
            "change_activitystatistics",
            "delete_activitystatistics",
            "view_activitystatistics",
            "add_comment",
            "change_comment",
            "delete_comment",
            "view_comment",
            "add_commentimage",
            "change_commentimage",
            "delete_commentimage",
            "view_commentimage",
            "add_supervision",
            "change_supervision",
            "delete_supervision",
            "view_supervision",
            "add_commentfiles",
            "change_commentfiles",
            "delete_commentfiles",
            "view_commentfiles",
            "add_failure",
            "change_failure",
            "delete_failure",
            "view_failure",
            "add_activitygroup",
            "change_activitygroup",
            "delete_activitygroup",
            "view_activitygroup",
            "add_activity",
            "change_activity",
            "delete_activity",
            "view_activity",
            "add_layout",
            "change_layout",
            "delete_layout",
            "view_layout",
            "add_user",
            "change_user",
            "delete_user",
            "view_user",
            "add_classifier",
            "change_classifier",
            "delete_classifier",
            "view_classifier",
            "add_organization",
            "change_organization",
            "delete_organization",
            "view_organization",
            "add_imagegallery",
            "change_imagegallery",
            "delete_imagegallery",
            "view_imagegallery",
        ],
        ConstantGroups.SUPERVISOR: [
            "add_activitystatistics",
            "change_activitystatistics",
            "view_activitystatistics",
            "add_comment",
            "change_comment",
            "view_comment",
            "add_commentimage",
            "change_commentimage",
            "view_commentimage",
            "add_supervision",
            "change_supervision",
            "view_supervision",
            "add_commentfiles",
            "change_commentfiles",
            "view_commentfiles",
            "add_failure",
            "change_failure",
            "view_failure",
            "view_activitygroup",
            "view_activity",
            "view_layout",
            "view_user",
            "view_classifier",
            "view_organization",
        ],
        ConstantGroups.WORKER: [
            "view_activitystatistics",
            "view_comment",
            "view_commentimage",
            "view_supervision",
            "view_commentfiles",
            "view_failure",
            "view_activitygroup",
            "view_activity",
            "view_layout",
            "view_user",
            "view_classifier",
            "view_organization",
        ],
    }

    for group_name, permission_codenames in groups_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)

        for codename in permission_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                print(f"Permission {codename} not found for group {group_name}")

        if created:
            print(f"Created group: {group_name}")
