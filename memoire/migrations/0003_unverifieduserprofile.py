# Generated by Django 5.1.3 on 2024-12-20 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memoire', '0002_alter_userprofile_password'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnverifiedUserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('prenom', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('sexe', models.CharField(choices=[('M', 'Masculin'), ('F', 'Féminin')], max_length=1)),
                ('type', models.CharField(max_length=50)),
                ('realisation_linkedin', models.URLField(blank=True, null=True)),
                ('photo_profil', models.ImageField(blank=True, null=True, upload_to='profiles/')),
                ('password', models.CharField(max_length=255)),
                ('verification_code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
