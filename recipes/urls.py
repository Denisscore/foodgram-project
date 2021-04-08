"""URL приложения recipes."""
from django.urls import path

from recipes import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index_view'),
    path('profile/<int:user_id>', views.ProfileView.as_view(),
         name='profile_view'),
    path('favorites', views.FavoriteView.as_view(), name='favorite_view'),
    path('favorites/<int:recipe_id>', views.FavoriteDelete.as_view(),
         name='favorite_delete'),
    path('subscriptions', views.Subscriptions.as_view(), name='subscriptions'),
    path('subscriptions/<int:author_id>', views.SubscriptionDelete.as_view(),
         name='subscription_delete'),
    path('followers/', views.FollowersView.as_view(), name='followers_view'),
    path('purchases', views.PurchaseView.as_view(), name='purchases_view'),
    path('purchases/<int:recipe_id>', views.PurchaseDelete.as_view(),
         name='purchase_delete'),
    path('shoplist', views.SendShopList.as_view(), name='shoplist'),
    path('ingredients/', views.GetIngredients.as_view(), name='ingredients'),
    path('new/', views.new_recipe_view, name='recipe_new_view'),
    path('recipes/<int:recipe_id>/edit', views.recipe_edit_view,
         name='recipe_edit_view'),
    path('recipes/<int:recipe_id>/delete', views.recipe_delete,
         name='recipe_delete'),
    path('recipes/<int:recipe_id>', views.recipe_item_view,
         name='recipe_view'),

]
