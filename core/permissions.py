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

        if request.user.is_staff:
            return True

        for (k, v) in getattr(view, "limited_fields", {}).items():
            d = request.data.get(k)
            if d in v:
                self.message = f"You are not permitted to set '{k}' field to '{d}'"
                return False

        return True


class IsCreatorOfParentOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it, and allow creation only if the user owns the parent object.
    The view should provide:
      - a `get_parent_for_permission(request)` method for create (POST) requests
      - a `parent_field` attribute or `get_parent(obj, request)` method for object-level checks
    """

    def has_permission(self, request, view):
        # Allow safe methods
        if request.method in permissions.SAFE_METHODS:
            return True

        # For create, check parent ownership using view's get_parent_for_permission
        if request.method == "POST":
            get_parent = getattr(view, "get_parent_for_permission", None)
            if callable(get_parent):
                parent = get_parent(request)
            else:
                parent = None
            if parent and hasattr(parent, "creator"):
                return parent.creator == request.user
            # If no parent or no creator, deny
            return False

        return True


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow creators of an object to edit it.
    The view should provide:
      - a `parent_field` attribute or `get_parent(obj, request)` method for object-level checks
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the creator of the object
        return hasattr(obj, "creator") and obj.creator == request.user