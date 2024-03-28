from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuctionProduct",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("price", models.DecimalField(decimal_places=3, max_digits=9)),
                ("description", models.TextField(blank=True, null=True)),
                ("bid_start_time", models.DateTimeField()),
                ("bid_end_time", models.DateTimeField()),
                ("is_closed", models.BooleanField(default=False)),
            ],
            options={"ordering": ["-created_date"], "abstract": False,},
        ),
        migrations.CreateModel(
            name="ProductPicture",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                ("image", models.ImageField(upload_to="images")),
                (
                    "product",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="product_pictures",
                        to="auctions.auctionproduct",
                    ),
                ),
            ],
            options={"ordering": ["-created_date"], "abstract": False,},
        ),
        migrations.CreateModel(
            name="Bid",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
                ("price", models.PositiveIntegerField()),
                ("time_stamp", models.DateTimeField(auto_now_add=True)),
                (
                    "auction_product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bids",
                        to="auctions.auctionproduct",
                    ),
                ),
                (
                    "bidder",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="bidders",
                        to="accounts.user",
                    ),
                ),
            ],
            options={
                "ordering": ["-time_stamp"],
                "unique_together": {("bidder", "auction_product")},
            },
        ),
    ]
