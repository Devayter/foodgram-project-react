# Generated by Django 4.2.6 on 2023-11-15 14:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0027_remove_ingredient_unique_name_measurement_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Наименование ингредиента'),
        ),
    ]