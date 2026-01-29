from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterView,
    LogoutView,
    ProfileView,
    SecretDocumentView,
    RoleViewSet,
    PermissionViewSet,
    ResourceViewSet,
    ActionViewSet,
)

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'resources', ResourceViewSet)
router.register(r'actions', ActionViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('profile/', ProfileView.as_view(), name='auth_profile'),
    path('secret/', SecretDocumentView.as_view(), name='secret_document'),
    path('admin/', include(router.urls)),
]
