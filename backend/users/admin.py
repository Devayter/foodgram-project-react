from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'recipe_count', 'subscribe_count')
    list_display_links = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('first_name', 'last_name',)
    search_fields = ('username', 'first_name', 'last_name',)
    empty_value_display = 'пусто'

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Количество рецептов'

    def subscribe_count(self, obj):
        return Subscribe.objects.filter(author=obj).count()
    subscribe_count.short_description = 'Количество подписчиков'


@admin.register(Subscribe)
class RecipetAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')
    list_display_links = ('author', 'subscriber')
    list_filter = ('author', 'subscriber')
    search_fields = ('author', 'subscriber')
    empty_value_display = 'пусто'
