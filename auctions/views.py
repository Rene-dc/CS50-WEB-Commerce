from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django import forms

from .models import User, Auction, Bid, Comment, Watchlist


def index(request):
    auctions = Auction.objects.all().order_by('-creation_date')
    bids = Bid.objects.all()

    # Get all highest bids
    last_bids = {}
    for bid in bids:
        last_bids[bid.item_id_id] = bid.last_price

    # Create dict for auctions with bids
    lists = []
    for auction in auctions:
        lists.append({
            'auction': auction,
            'last_bid': last_bids.get(auction.id, auction.starting_price),
            'category_name': dict(Auction.CATEGORIES_CHOICES)[auction.category]
        })
    return render(request, "auctions/index.html", {
        "lists": lists,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


class NewAuctionForm(forms.ModelForm):
    description = forms.CharField(label='Description', widget=forms.Textarea())
    image_link = forms.URLField(label='Image URL', required=False, widget=forms.URLInput())

    class Meta:
        model = Auction
        fields = ['title', 'category', 'starting_price', 'description', 'image_link']


def create(request):
    if request.method == "POST":
        form = NewAuctionForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.seller = request.user
            data.save()
            return HttpResponseRedirect(reverse("index"))
        else: 
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create.html", {
            "form": NewAuctionForm()
        })


def itemview(request, item):
    auction = Auction.objects.get(pk=item)
    bid = Bid.objects.filter(item_id=item)
    comments = Comment.objects.filter(auction_id=item).order_by('-date')
    if bid:
        bid = bid.first
    watchlist = Watchlist.objects.filter(auction_id=item, user_id=request.user.id)
    if watchlist:
        watchlist = watchlist.first()
    category = dict(Auction.CATEGORIES_CHOICES)[auction.category]
    return render(request, "auctions/itemview.html", {
        "auction": auction,
        "bid": bid,
        "category": category,
        "watchlist": watchlist,
        "comments": comments
    })


def watchlist_add(request):
    if request.method == "POST":
        item = get_object_or_404(Auction, pk=request.POST["idauction"])
        user = User.objects.get(pk=request.user.id)
        watch = Watchlist(user_id=user, auction_id=item)
        watch.save()
        return HttpResponseRedirect(reverse("itemview", args=(request.POST["idauction"])))
    else:
        return HttpResponseRedirect(reverse("index"))


def watchlist_remove(request):
    if request.method == "POST":
        item = get_object_or_404(Auction, pk=request.POST["idauction"])
        user = User.objects.get(pk=request.user.id)
        object = Watchlist.objects.get(user_id=user, auction_id=item)
        object.delete()
        return HttpResponseRedirect(reverse("itemview", args=(request.POST["idauction"])))
    else:
        return HttpResponseRedirect(reverse("index"))


def closebid(request):
    if request.method == "POST":
        item = get_object_or_404(Auction, pk=request.POST["idauction"])
        user_id = User.objects.get(username=item.seller)
        user_id = user_id.id
        print(user_id)
        print(request.user.id)
        # If user is seller
        if request.user.id == user_id:
            item.active = 0
            item.save()
        return HttpResponseRedirect(reverse("itemview", args=(request.POST["idauction"])))
    else:
        return HttpResponseRedirect(reverse("index"))


def placebid(request):
    if request.method == "POST":
        item = get_object_or_404(Auction, pk=request.POST["idauction"])
        user = User.objects.get(pk=request.user.id)

        # Convert to float (check if it is not text)
        try:
            bid_amount = float(request.POST["newbid"])
        except ValueError:
            messages.error(request, "An error occured with your bid.")
            return HttpResponseRedirect(reverse("itemview", args=[request.POST["idauction"]]))
        bid_amount = round(bid_amount, 2)

        # Get last price
        try:
            current_price = Bid.objects.get(item_id=item)
            current_price = current_price.last_price
            marker = 1
        except Bid.DoesNotExist:
            current_price = item.starting_price
            marker = 0

        # Check if bid is higher than last price
        if bid_amount >= (current_price + 0.1):
            if marker == 0:
                newbid = Bid(item_id=item, buyer_id=user, last_price=bid_amount, bids_count=1)
                newbid.save()
            elif marker == 1:
                newbid = Bid.objects.get(item_id=item, buyer_id=user)
                newbid.last_price = bid_amount
                newbid.bids_count += 1
                newbid.save()
        else:
            messages.error(request, "Your bid was too low !")
            return HttpResponseRedirect(reverse("itemview", args=[request.POST["idauction"]]))
        messages.success(request, "Your bid was resgistered successfully.")
        return HttpResponseRedirect(reverse("itemview", args=[request.POST["idauction"]]))
    else:
        return HttpResponseRedirect(reverse("index"))


def addcomment(request):
    if request.method == "POST":
        item = get_object_or_404(Auction, pk=request.POST["idauction"])
        user = User.objects.get(pk=request.user.id)
        text = request.POST["comment"]
        if text:
            if len(text) > 512:
                messages.warning(request, "Your comment is too long.")
                return HttpResponseRedirect(reverse("itemview", args=(request.POST["idauction"])))
            else:
                newcomment = Comment(user_id=user, auction_id=item, comment=text)
                newcomment.save()
        return HttpResponseRedirect(reverse("itemview", args=(request.POST["idauction"]))) 
    else:
        return HttpResponseRedirect(reverse("index"))


def watchlist(request):
    if request.user.id:
        user = User.objects.get(pk=request.user.id)
        favorites = Watchlist.objects.filter(user_id=user)
        auctions = Auction.objects.filter()
        bids = Bid.objects.all()

        # Get all highest bids
        last_bids = {}
        for bid in bids:
            last_bids[bid.item_id_id] = bid.last_price

        # Create dict for auctions with bids
        lists = []
        for auction in auctions:
            for favorite in favorites:
                if auction.id == favorite.auction_id_id:
                    lists.append({
                        'auction': auction,
                        'last_bid': last_bids.get(auction.id, auction.starting_price),
                        'category_name': dict(Auction.CATEGORIES_CHOICES)[auction.category]
                    })
        return render(request, "auctions/watchlist.html", {
            "lists": lists,
        })
    else:
        messages.error(request, "You must log in add items to your watchlist.")
        return HttpResponseRedirect(reverse('index'))


def categories(request):
    list = []
    categories = Auction.CATEGORIES_CHOICES
    for category in categories:
        list.append({
            'cat': category[0],
            'category': category[1]})
    return render(request, "auctions/categories.html", {
        'list': list,
    })


def category(request, item):
    cat_full_name = dict(Auction.CATEGORIES_CHOICES)[item]
    auctions = Auction.objects.filter(category=item).order_by('-creation_date')
    bids = Bid.objects.all()

    # Get all highest bids
    last_bids = {}
    for bid in bids:
        last_bids[bid.item_id_id] = bid.last_price
    # Create dict for auctions with bids
    lists = []
    for auction in auctions:
        lists.append({
            'auction': auction,
            'last_bid': last_bids.get(auction.id, auction.starting_price),
            'category_name': dict(Auction.CATEGORIES_CHOICES)[auction.category]
        })
    return render(request, "auctions/category.html", {
        "lists": lists,
        "cat_full_name": cat_full_name,
    })

