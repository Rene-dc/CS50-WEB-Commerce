from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass


class Auction(models.Model):
    ART = 'AR'
    BOOKS = 'BO'
    CLOTHING = 'CL'
    ELECTRONICS = 'EL'
    GARDEN = 'GA'
    HOME = 'HO'
    JEWELRY = 'JE'
    MUSIC = 'MU'
    MOTORS = 'MO'
    OTHER = 'OT'
    SPORTING = 'SP'
    CATEGORIES_CHOICES = [
        (ART, 'Art'),
        (BOOKS, 'Books'),
        (CLOTHING, 'Clothing'),
        (ELECTRONICS, 'Electronics'),
        (GARDEN, 'Garden'),
        (HOME, 'Home'),
        (JEWELRY, 'Jewelry'),
        (MOTORS, 'Motors'),
        (MUSIC, 'Music'),
        (OTHER, 'Other'),
        (SPORTING, 'Sporting'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=512)
    category = models.CharField(max_length=2, choices=CATEGORIES_CHOICES)
    starting_price = models.FloatField(max_length=12, validators=[MinValueValidator(0.1)])
    image_link = models.CharField(max_length=128, default="https://t3.ftcdn.net/jpg/04/62/93/66/360_F_462936689_BpEEcxfgMuYPfTaIAOC1tCDurmsno7Sp.jpg")
    creation_date = models.DateTimeField(auto_now_add=True)
    active = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.id}: {self.title} in {self.category} category"


class Bid(models.Model):
    item_id = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids_id")
    buyer_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    last_price = models.FloatField(max_length=12)
    bids_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Auction n°{self.item_id}: {self.bids_count} bids, current price: {self.last_price}$"


class Comment(models.Model):
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="reference_id")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user_id")
    date = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=512)


class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sellerwatch")
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auctionwatch")
