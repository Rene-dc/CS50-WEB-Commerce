from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("view/<str:item>", views.itemview, name="itemview"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist_add", views.watchlist_add, name="watchlist_add"),
    path("watchlist_remove", views.watchlist_remove, name="watchlist_remove"),
    path("categories", views.categories, name="categories"),
    path("cat/<str:item>", views.category, name="category"),
    path("addcomment", views.addcomment, name="addcomment"),
    path("placebid", views.placebid, name="placebid"),
    path("closebid", views.closebid, name="closebid"),
    path("create", views.create, name="create"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
