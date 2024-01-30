# Generated by Django 5.0.1 on 2024-01-30 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AwsPathBucket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path_sniffer', models.CharField(max_length=100, verbose_name='Path Sniffer')),
                ('path_name', models.CharField(max_length=100, verbose_name='Path Name')),
                ('path_internal_date', models.DateTimeField(blank=True, null=True, verbose_name='Path Date')),
                ('path_reveal_date', models.DateTimeField(blank=True, null=True, verbose_name='Path Date')),
                ('path_status', models.BooleanField(default=False, verbose_name='Path Status')),
            ],
            options={
                'verbose_name': 'Aws Path Bucket',
                'verbose_name_plural': 'Aws Path Buckets',
                'ordering': ['path_sniffer'],
            },
        ),
    ]