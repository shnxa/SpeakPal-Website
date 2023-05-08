from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from . import views


urlpatterns = [
    path('', views.UserListApiView.as_view()),
    path('<int:id>/', views.UserDetailApiView.as_view()),
    path('register/', views.RegistrationView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('password_reset/', views.PasswordResetView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('login-success/', views.LoginSuccess.as_view()),
    path('friends/',  # GET (requires Auth) returns Friends by id of user
         views.FriendsListView.as_view()),
    path('friends/<int:pk>/', views.FriendsDeleteView.as_view()),

    path('<int:pk>/send_friend_request/',
         views.SendFriendRequestView.as_view(),
         name='send friend request'),
    path('<int:pk>/block_user/', views.BlockUserView.as_view()),
    path('friend_requests/',
         views.FriendRequestsListView.as_view()),
    path('friend_requests/<int:pk>/',
         views.HandleFriendRequestView.as_view(),
         name='accept friend request'),
    path('blacklist/', TokenBlacklistView.as_view()),

]
