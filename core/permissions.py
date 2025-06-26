from rest_framework import permissions

class LimitedFieldEditPermission(permissions.BasePermission):
    '''
    This permission will limit the field edit's to a certain value,
    when used it will pervent un admin user to edit a filed with pre
    defined value.

    View class needs to have an field `limited_fields`
    Example Usage:
    ```python
    limited_fields = {
        "status": ["published"]
    }
    ```
    In this example when the un admin user send a request with status field set to
    published the permission will be denied.
    '''

    message = ""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        for (k, v) in view.limited_fields.items():
            d = request.data.get(k)
            if d and d in v:
                self.message = f"You don't have permission to set '{k}' field to '{d}'"
                return False

        return True

