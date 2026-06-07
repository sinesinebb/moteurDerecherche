from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission pour s'assurer que l'utilisateur n'accède qu'à ses propres données.
    """
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission qui permet la lecture à tous mais l'écriture uniquement au propriétaire.
    """
    
    def has_object_permission(self, request, view, obj):
        # Les méthodes de lecture sont autorisées pour tout le monde
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # L'écriture est réservée au propriétaire
        return obj.user == request.user