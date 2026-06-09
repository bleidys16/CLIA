from rest_framework.permissions import BasePermission

class IsAdministrador(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.rol == 'ADMIN'

class IsAnalista(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.rol == 'ANALISTA'

class IsMedico(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'perfil') and request.user.perfil.rol == 'MEDICO'
