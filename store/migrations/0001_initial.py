# Generated by Django 4.1.1 on 2022-09-22 18:04

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('editable', models.BooleanField(default=True)),
                ('is_primary', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=500)),
                ('mobile', models.CharField(max_length=20)),
                ('landline', models.CharField(blank=True, max_length=20, null=True)),
                ('address1', models.CharField(max_length=2000)),
                ('address2', models.CharField(blank=True, max_length=2000, null=True)),
                ('landmark', models.CharField(max_length=1000)),
                ('pincode', models.CharField(max_length=20)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='address', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Address Entries',
                'ordering': ['first_name', 'last_name'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=300, null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('percent', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=1000, unique=True, upload_to='images/product-images/')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'ordering': ['key'],
            },
        ),
        migrations.CreateModel(
            name='KeyValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.key')),
            ],
            options={
                'verbose_name_plural': 'Key-Value-Pairs',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(1)])),
                ('amount_payable', models.DecimalField(decimal_places=2, max_digits=20, validators=[django.core.validators.MinValueValidator(1)])),
                ('order_status', models.CharField(choices=[('O', 'OPEN'), ('C', 'CLOSED'), ('N', 'CANCELLED'), ('P', 'PENDING_CANCELLATION'), ('F', 'FAILED')], default='O', max_length=1)),
                ('payment_method', models.CharField(choices=[('CCD', 'Credit Card'), ('DCD', 'Debit Card'), ('PPL', 'PayPal'), ('OTH', 'Other'), ('COD', 'Cash On Delivery')], default='COD', max_length=3)),
                ('payment_status', models.CharField(choices=[('P', 'Pending'), ('S', 'Successful'), ('F', 'Failed'), ('U', 'Unsuccessful')], default='P', max_length=1)),
                ('placed_at', models.DateTimeField(auto_now_add=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('expected_delivery_time', models.DateTimeField(blank=True, null=True)),
                ('count', models.IntegerField(default=1)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='store.address')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to=settings.AUTH_USER_MODEL)),
                ('discount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='store.discount')),
            ],
            options={
                'ordering': ['-placed_at'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=255, null=True)),
                ('categories', models.ManyToManyField(blank=True, related_name='products', to='store.category')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'ordering': ['value'],
            },
        ),
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=1, max_digits=20, validators=[django.core.validators.MinValueValidator(1)])),
                ('unit', models.CharField(default='Kg', max_length=10)),
                ('availability', models.BooleanField(default=True)),
                ('info', models.TextField(blank=True, max_length=1000, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('inventory', models.IntegerField(default=0)),
                ('delivery_time_in_days', models.IntegerField(default=1)),
                ('discount', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='store.discount')),
                ('images', models.ManyToManyField(blank=True, related_name='variations', to='store.image')),
                ('keyvalues', models.ManyToManyField(blank=True, to='store.keyvalue')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variations', to='store.product')),
            ],
            options={
                'ordering': ['product'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='products', to='store.tag'),
        ),
        migrations.CreateModel(
            name='Pincode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pincode', models.CharField(max_length=10, unique=True)),
                ('delivery_time_in_days', models.IntegerField(default=1)),
                ('products_unavailable', models.ManyToManyField(blank=True, related_name='pincodes', to='store.variation')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=6)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('discount_percent', models.IntegerField(blank=True, null=True)),
                ('amount_payable', models.DecimalField(decimal_places=2, max_digits=20)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orderitems', to='store.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orderitems', to='store.variation')),
            ],
            options={
                'ordering': ['-order__placed_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderCancellation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(blank=True, max_length=1000, null=True)),
                ('cancelled_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='cancellation', to='store.order')),
            ],
            options={
                'ordering': ['-cancelled_at'],
            },
        ),
        migrations.AddField(
            model_name='keyvalue',
            name='value',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.value'),
        ),
        migrations.AddField(
            model_name='key',
            name='values',
            field=models.ManyToManyField(through='store.KeyValue', to='store.value'),
        ),
    ]
