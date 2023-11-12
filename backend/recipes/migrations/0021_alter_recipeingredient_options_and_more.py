# Generated by Django 4.2.6 on 2023-11-12 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_favorites_unique_recipe_user_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'Рецепт и Ингредиент', 'verbose_name_plural': 'Рецепты и Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='recipetag',
            options={'verbose_name': 'Рецепт и Тэг', 'verbose_name_plural': 'Рецепты и Тэги'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Тэг', 'verbose_name_plural': 'Тэги'},
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to='images', verbose_name='Фото блюда'),
        ),
    ]
