# Generated by Django 4.2.6 on 2023-11-06 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_alter_recipe_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='media/recipes/images', verbose_name='Фото блюда'),
        ),
    ]
