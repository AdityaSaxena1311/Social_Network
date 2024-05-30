from django.urls import path
from .views import signup, login, search_users, send_friend_request, handle_friend_request, list_friends, list_pending_requests

urlpatterns = [
    path('signup/', signup),
    path('login/', login),
    path('search/', search_users),
    path('friend-request/<int:to_user_id>/', send_friend_request),
    path('handle-request/<int:request_id>/<str:action>/', handle_friend_request),
    path('friends/', list_friends),
    path('pending-requests/', list_pending_requests),
]
