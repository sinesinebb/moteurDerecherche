from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission personnalisée pour autoriser uniquement le propriétaire ou un administrateur.
    """
    
    def has_object_permission(self, request, view, obj):
        # L'administrateur a tous les droits
        if request.user.is_superuser:
            return True
        
        # L'utilisateur peut accéder à son propre objet
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'id'):
            return obj.id == request.user.id
        
        return False


class IsAdmin(permissions.BasePermission):
    """
    Permission réservée aux administrateurs.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser