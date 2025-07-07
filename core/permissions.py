from rest_framework import permissions

class LimitedFieldEditPermission(permissions.BasePermission):
    """
    Prevents non-admin users from setting certain fields to restricted values.

    The view class should define a `limited_fields` attribute, e.g.:
    limited_fields = {
        "status": ["published"]
    }
    If a non-admin user attempts to set a restricted value, permission is denied.
    """
    message = ""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        for field, restricted_values in getattr(view, "limited_fields", {}).items():
            value = request.data.get(field)
            if value in restricted_values:
                self.message = f"You are not permitted to set '{field}' field to '{value}'"
                return False
        return True

class IsCreatorOfParentOrReadOnly(permissions.BasePermission):
    """
    Allows editing only by the creator of an object, and allows creation only if the user owns the parent object.

    The view should provide:
      - a `get_parent_for_permission(request)` method for create (POST) requests
      - a `parent_field` attribute or `get_parent(obj, request)` method for object-level checks
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == "POST":
            get_parent = getattr(view, "get_parent_for_permission", None)
            parent = get_parent(request) if callable(get_parent) else None
            if parent and hasattr(parent, "creator"):
                return parent.creator == request.user
            return False
        return True

class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Allows editing only by the creator of an object.
    The view should provide a `parent_field` attribute or `get_parent(obj, request)` method for object-level checks.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(obj, "creator") and obj.creator == request.user