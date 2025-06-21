# Generated manually for Open Library integration

from django.db import migrations, models
import django.db.models.deletion
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        # Utwórz tabele tylko jeśli nie istnieją
        migrations.RunSQL(
            """
            -- Tabela PredictionRequest
            CREATE TABLE IF NOT EXISTS ml_api_predictionrequest (
                id BIGSERIAL PRIMARY KEY,
                feature1 DOUBLE PRECISION NOT NULL,
                feature2 DOUBLE PRECISION NOT NULL,
                feature3 DOUBLE PRECISION NOT NULL,
                feature4 DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Tabela PredictionResult
            CREATE TABLE IF NOT EXISTS ml_api_predictionresult (
                id BIGSERIAL PRIMARY KEY,
                prediction DOUBLE PRECISION NOT NULL,
                confidence DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                request_id BIGINT NOT NULL UNIQUE REFERENCES ml_api_predictionrequest(id) ON DELETE CASCADE
            );
            
            -- Tabela books - TYLKO Open Library, bez Google Books
            CREATE TABLE IF NOT EXISTS books (
                id BIGSERIAL PRIMARY KEY,
                isbn VARCHAR(20) UNIQUE,
                title VARCHAR(500) NOT NULL,
                author VARCHAR(300),
                publisher VARCHAR(200),
                publication_year INTEGER,
                image_url_s VARCHAR(500),
                image_url_m VARCHAR(500),
                image_url_l VARCHAR(500),
                description TEXT,
                categories TEXT[],
                page_count INTEGER,
                language VARCHAR(10) DEFAULT 'en',
                average_rating DECIMAL(3,2),
                ratings_count INTEGER DEFAULT 0,
                open_library_id VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Indeksy
            CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
            CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
            CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
            CREATE INDEX IF NOT EXISTS idx_books_open_library_id ON books(open_library_id);
            """,
            reverse_sql=migrations.RunSQL.noop
        ),
        
        # Modele Django
        migrations.CreateModel(
            name='PredictionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature1', models.FloatField()),
                ('feature2', models.FloatField()),
                ('feature3', models.FloatField()),
                ('feature4', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'ml_api_predictionrequest',
            },
        ),
        migrations.CreateModel(
            name='PredictionResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prediction', models.FloatField()),
                ('confidence', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='ml_api.predictionrequest')),
            ],
            options={
                'db_table': 'ml_api_predictionresult',
            },
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ('title', models.CharField(max_length=500)),
                ('author', models.CharField(blank=True, max_length=300, null=True)),
                ('publisher', models.CharField(blank=True, max_length=200, null=True)),
                ('publication_year', models.IntegerField(blank=True, null=True)),
                ('image_url_s', models.URLField(blank=True, max_length=500, null=True)),
                ('image_url_m', models.URLField(blank=True, max_length=500, null=True)),
                ('image_url_l', models.URLField(blank=True, max_length=500, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('categories', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None)),
                ('page_count', models.IntegerField(blank=True, null=True)),
                ('language', models.CharField(blank=True, default='en', max_length=10, null=True)),
                ('average_rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('ratings_count', models.IntegerField(blank=True, default=0, null=True)),
                ('open_library_id', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'books',
                'ordering': ['-created_at'],
            },
        ),
    ]