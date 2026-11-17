from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from core.crud import Module

from .forms import LoginForm, PasswordForm, UserCreateForm, UserUpdateForm
from .models import User

app_name = "accounts"

module = Module(
    User,
    namespace=app_name,
    prefix="user_",
    title="User Accounts",
    icon="shield-lock-fill",
    order=200,
    fields=["username", "first_name", "last_name", "email", "role", "account_status"],
    list_display=["username", "first_name", "last_name", "email", "role", "account_status",
                  "last_login"],
    detail_fields=["username", "first_name", "last_name", "email", "role", "account_status",
                   "is_superuser", "date_joined", "last_login"],
    search_fields=["username", "first_name", "last_name", "email"],
    list_filter="role",
    roles=[],  # administrators only
)

list_view, detail_view, create_view, update_view, delete_view = module.make_views()
create_view.form_class = UserCreateForm
update_view.form_class = UserUpdateForm

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(
        template_name="registration/login.html", authentication_form=LoginForm,
        redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password/", auth_views.PasswordChangeView.as_view(
        template_name="registration/password_change.html", form_class=PasswordForm,
        success_url=reverse_lazy("core:dashboard")), name="password_change"),
    path("users/", list_view.as_view(), name="user_list"),
    path("users/new/", create_view.as_view(), name="user_create"),
    path("users/<int:pk>/", detail_view.as_view(), name="user_detail"),
    path("users/<int:pk>/edit/", update_view.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", delete_view.as_view(), name="user_delete"),
]
