# Generated by Django 4.0.5 on 2022-06-13 22:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={},
        ),
        migrations.AlterModelOptions(
            name='creator',
            options={},
        ),
        migrations.AlterModelOptions(
            name='interviewee',
            options={},
        ),
        migrations.AlterModelOptions(
            name='item',
            options={},
        ),
        migrations.AlterModelOptions(
            name='option',
            options={},
        ),
        migrations.AlterModelOptions(
            name='precondition',
            options={},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={},
        ),
        migrations.AlterModelOptions(
            name='section',
            options={},
        ),
        migrations.AlterModelOptions(
            name='submission',
            options={},
        ),
        migrations.AlterModelOptions(
            name='survey',
            options={},
        ),
        migrations.AlterModelOptions(
            name='surveysent',
            options={},
        ),
        migrations.AlterModelTable(
            name='submission',
            table='submissions',
        ),
    ]