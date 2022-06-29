# Generated by Django 4.0.5 on 2022-06-29 18:50

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_submission_hash_alter_surveysent_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='surveysent',
            name='sent_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='answer',
            name='option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='api.option'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='survey',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.survey'),
        ),
    ]