from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS


class RegistrationPermission(BasePermission):
    """
    允许未认证用户访问注册 API。
    """

    def has_permission(self, request, view):
        return True  # 允许所有用户访问注册 API


class LoginPermission(BasePermission):
    """
    允许通过 Basic 认证的用户访问登录页面。
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated or request.method == 'POST'  # 仅允许已认证用户或 POST 请求访问登录页面


class DefaultPermission(BasePermission):
    """
    默认权限，要求用户通过 Token 认证。
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
