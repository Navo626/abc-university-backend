# Generated by Django 5.0 on 2023-12-16 04:39

from django.db import migrations, models

import api.models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0010_remove_lecturer_image_user_image_alter_student_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecturer',
            name='image',
            field=models.ImageField(null=True, upload_to=api.models.upload_to, verbose_name='Image'),
        ),
    ]
