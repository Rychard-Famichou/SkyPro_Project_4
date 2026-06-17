from django.urls import path

from users.views import UserAdminListView, UserAdminDetailView, UserToggleActiveView

app_name = 'users'

urlpatterns = [
    path('user_list/', UserAdminListView.as_view(), name='user_list'),
    path('user_detail/<int:pk>/', UserAdminDetailView.as_view(), name='user_detail'),
    path('user_detail/<int:pk>/toggle-active/', UserToggleActiveView.as_view(), name='user_toggle_active'),
]
