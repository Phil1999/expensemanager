# Generated by Django 3.2.7 on 2021-10-02 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userpreferences', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpreference',
            name='currency',
            field=models.CharField(default='USD - United States Dollar', max_length=255),
        ),
    ]
