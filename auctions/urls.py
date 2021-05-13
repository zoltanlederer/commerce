from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("inactive_listing", views.inactive_listing, name="inactive_listing"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("item<int:item_id>", views.item, name="item"),
    path("createwatchlist", views.createWatchList, name="createWatchList"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category"),
    path("comment", views.comment, name="comment"),
    path("bid", views.bid, name="bid"),
]
