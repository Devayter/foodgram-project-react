# Generated by Django 4.2.6 on 2023-11-06 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0013_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='', verbose_name='Фото блюда'),
        ),
    ]