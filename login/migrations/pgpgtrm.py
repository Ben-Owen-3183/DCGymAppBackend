from django.db import migrations

class Migration(migrations.Migration):

    operations = [
        migrations.RunSQL('CREATE EXTENSION IF NOT EXISTS pg_trgm'),
    ]