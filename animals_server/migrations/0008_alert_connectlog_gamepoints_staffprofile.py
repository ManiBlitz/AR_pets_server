# Generated by Django 2.2.1 on 2019-08-14 19:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('animals_server', '0007_auto_20190622_1353'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConnectLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipinfo_all', models.TextField(blank=True)),
                ('username_used', models.CharField(max_length=200)),
                ('time_collect', models.DateTimeField(auto_now_add=True)),
                ('connection_result', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='StaffProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=40, unique=True)),
                ('date_creation', models.DateField(auto_now_add=True)),
                ('user_name', models.CharField(max_length=200, unique=True)),
                ('ipinfo_all', models.TextField(blank=True)),
                ('auth_level', models.IntegerField(default=1)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('pwd', models.CharField(max_length=200)),
                ('last_pwd_change', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='GamePoints',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_type', models.CharField(max_length=200)),
                ('time_end_game', models.DateTimeField(auto_now_add=True)),
                ('total_points', models.DecimalField(decimal_places=5, default=0.0, max_digits=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='animals_server.User')),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_alert', models.CharField(max_length=200)),
                ('log_time', models.DateTimeField(auto_now_add=True)),
                ('visited', models.BooleanField(default=False)),
                ('threat_level', models.IntegerField(default=0)),
                ('ip_computer', models.CharField(max_length=200)),
                ('connect_log',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='animals_server.ConnectLog')),
            ],
        ),
    ]
