# Generated by Django 2.0 on 2022-11-16 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_voting_escaños'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voting',
            name='escaños',
            field=models.PositiveIntegerField(),
        ),
    ]
