# Generated by Django 4.2.6 on 2023-11-05 13:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_rename_title_recipe_name_alter_recipe_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
    ]
