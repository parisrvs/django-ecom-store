# Generated by Django 4.1 on 2022-09-08 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_orderitem_quantity'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['name']},
        ),
    ]