# Generated by Django 5.1.5 on 2025-01-31 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cinemas", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actor",
            name="id",
            field=models.BigIntegerField(
                primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="genre",
            name="id",
            field=models.BigIntegerField(
                primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="movie",
            name="id",
            field=models.BigIntegerField(
                primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="showtime",
            name="id",
            field=models.BigIntegerField(
                primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
