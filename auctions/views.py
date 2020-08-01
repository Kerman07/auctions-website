from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Bid, User, Listing, Watchlist, Comment
from .forms import ListingForm, BidForm


def index(request):
    active = Listing.objects.filter(active=True).order_by('-created')
    watching = 0
    if request.user.is_authenticated:
        watching = Watchlist.objects.filter(user=request.user).count()
    return render(request, "auctions/index.html", {
        "active": active, "watching": watching
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user:
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


@login_required
def create_listing(request):
    form = ListingForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.author = request.user
        obj.save()
        return redirect(reverse('index'))
    return render(request, 'auctions/create_listing.html', {
        'form': form
    })


def listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return render(request, 'auctions/404.html')
    if not request.user.is_authenticated:
        return render(request, 'auctions/listing.html', {
            'listing': listing
        })
    watching = 0
    if request.user.is_authenticated:
        watching = Watchlist.objects.filter(user=request.user).count()
    owner, error = False, ''
    won_bid, last_bid_by = False, False
    in_watchlist = Watchlist.objects.filter(
        user=request.user).filter(listing=listing).first()
    comments = Comment.objects.filter(listing=listing).order_by('-created')
    bid_number = Bid.objects.filter(listing=listing).count()
    if in_watchlist:
        is_watching = True
    else:
        is_watching = False
    if request.user == listing.author:
        owner = True
    if not owner:
        last_bid = Bid.objects.filter(
            listing=listing).order_by('-created').first()
        if last_bid and last_bid.user == request.user:
            if not listing.active:
                won_bid = True
            else:
                last_bid_by = True
    if request.method == "POST":
        if 'price' in request.POST:
            cur_price = Listing.objects.get(id=listing_id).price
            bid_price = request.POST.get('price')
            if float(bid_price) > cur_price:
                bid = Bid()
                bid.listing = Listing.objects.get(id=listing_id)
                bid.user = request.user
                bid.price = float(bid_price)
                bid.save()
                listing = Listing.objects.get(id=listing_id)
                listing.price = float(bid_price)
                listing.save()
                bid_number = Bid.objects.filter(listing=listing).count()
            else:
                error = 'The bid must be higher than the current price!'
            return render(request, 'auctions/listing.html', {
                'listing': listing, 'form': BidForm(), 'owner': owner,
                'error': error, 'watching': watching, 'won_bid': won_bid,
                'comments': comments, 'last_bid_by': last_bid_by,
                'bid_number': bid_number, 'is_watching': is_watching
            })
        elif 'close' in request.POST:
            listing.active = False
            listing.save()
            return redirect(reverse('index'))
        elif 'watchlist-add' in request.POST:
            watchlist = Watchlist()
            watchlist.user = request.user
            watchlist.listing = listing
            watchlist.save()
            return(redirect('listing', listing_id))
        elif 'watchlist-remove' in request.POST:
            in_watchlist.delete()
            return(redirect('listing', listing_id))
        elif 'comment' in request.POST:
            content = request.POST.get('comment')
            comment = Comment()
            comment.content = content
            comment.user = request.user
            comment.listing = listing
            comment.save()
            return(redirect('listing', listing_id))
    return render(request, 'auctions/listing.html', {
        'listing': listing, 'form': BidForm(), 'owner': owner,
        'error': error, 'watching': watching, 'won_bid': won_bid,
        'comments': comments, 'last_bid_by': last_bid_by,
        'bid_number': bid_number, 'is_watching': is_watching
    })


def user_profile(request, user_id):
    watching = 0
    if request.user.is_authenticated:
        watching = Watchlist.objects.filter(user=request.user).count()
    user = User.objects.get(id=user_id)
    listings = Listing.objects.filter(author=user).order_by('-created')
    return render(request, 'auctions/user_profile.html', {
        'listings': listings, 'user': user, 'watching': watching
    })


def watchlist(request):
    watched = Watchlist.objects.filter(user=request.user).all()
    active = sorted([en.listing for en in watched],
                    key=lambda x: x.created, reverse=True)
    watching = 0
    if request.user.is_authenticated:
        watching = Watchlist.objects.filter(user=request.user).count()
    return render(request, 'auctions/watchlist.html', {
        'active': active, 'watching': watching
    })


def categories(request):
    watching = 0
    if request.user.is_authenticated:
        watching = Watchlist.objects.filter(user=request.user).count()
    cats = Listing.objects.filter(
        active=True).order_by().values_list('category', flat=True).distinct()
    return render(request, 'auctions/categories.html', {
        'cats': cats, 'watching': watching
    })


def category(request, category):
    active = Listing.objects.filter(category=category).filter(
        active=True).order_by('-created')
    watching = 0
    if request.user.is_authenticated:
        watching = Watchlist.objects.filter(user=request.user).count()
    return render(request, 'auctions/category.html', {
        'active': active, 'category': category, 'watching': watching
    })
