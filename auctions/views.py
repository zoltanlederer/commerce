from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max

from .models import User, ActiveListing, WatchList, Comments, Bids
from decimal import Decimal


def index(request):
    listings = ActiveListing.objects.filter(active=True).order_by('-id')

    return render(request, "auctions/index.html", {
        'listings': listings, 'active': True
    })

def inactive_listing(request):
    listings = ActiveListing.objects.filter(active=False).order_by('-id')

    return render(request, "auctions/index.html", {
        'listings': listings, 'active': False
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


def create(request):
    if request.method == 'POST':
        if request.POST.get('title'):
            # A small server side form validation only for the length of the inputs
            if len(request.POST.get('title')) < 64 and \
                len(request.POST.get('short-description')) < 256 and \
                len(request.POST.get('description')) < 356 and \
                len(request.POST.get('price')) < 10 and \
                len(request.POST.get('image')) < 500 and \
                len(request.POST.get('category')) < 32:
                    create = ActiveListing()
                    create.title = request.POST.get('title')
                    create.shortDescription = request.POST.get('short-description')
                    create.description = request.POST.get('description')
                    create.price = request.POST.get('price')

                    if request.POST.get('image') == '':
                        create.image = 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/495px-No-Image-Placeholder.svg.png'
                    else: 
                        create.image = request.POST.get('image')

                    create.category = request.POST.get('category')
                    create.created = request.user
                    create.save()

                    return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "auctions/create.html")

    return render(request, "auctions/create.html")


def item(request, item_id):
    # Current logged in user
    user = request.user
    
    # Select (get) the item from the database
    item = ActiveListing.objects.get(id=item_id)

    # Check if the item and the username are in the watchlist database (same row)
    itemIsInWatchlist = WatchList.objects.filter(items=item_id) & WatchList.objects.filter(user=user)

    # Change to the correct text on the add/remove watchlist button
    watchlistBtnMsg = ''
    if itemIsInWatchlist.exists():
        watchlistBtnMsg = 'Remove Watchlist'
    elif itemIsInWatchlist.exists() == False:
        watchlistBtnMsg = 'Add Watchlist'
   
    #Give 'HTML5 notification' to user if the wished bid is too low, and update the current price after bid
    startingPrice = item.price
    getHighestBid = Bids.objects.filter(item=item_id).last()
    if getHighestBid == None:
        highestBidCheck = round(float(startingPrice) + 0.01, 2)
        # currentPrice = float(startingPrice)
    else:
        highestBidCheck = round(float(getHighestBid.bid) + 0.01, 2)
        # Update price in the Active List database
        newPrice = round(getHighestBid.bid, 2)
        ActiveListing.objects.filter(id=item_id).update(price=newPrice)


    # Check if the item and the username are in the bid database (same row)
    bidWinner = ''
    # If user exist
    if user.is_authenticated: 
        itemIsInBid = Bids.objects.filter(item=item_id) & Bids.objects.filter(user=user)
        if itemIsInBid.exists():
            # Check who is the winner of the auction
            lastBidUser = Bids.objects.filter(item=item_id).last()
            bidWinner = str(lastBidUser.user)
        elif itemIsInBid.exists() == False:
            bidWinner = ''


    # All the bids for the selected item
    bids = Bids.objects.filter(item=item_id)

    # Save only the last five bids
    lastFiveBid = 0
    if len(bids) > 0 and len(bids) < 5:
        lastFiveBid = reversed(bids)
    elif len(bids) >= 5:
        lastFiveBid = reversed(bids[len(bids)-5:len(bids)])
        

    # All the comments for the selected item
    comments = Comments.objects.filter(item=item_id)
 
    return render(request, 'auctions/item.html', {
        'item': item, 'user': user, 'watchlistBtnMsg': watchlistBtnMsg, 
        'comments': comments, 'bids': bids, 'bidWinner': bidWinner,
        'getHighestBid': getHighestBid, 'highestBidCheck': highestBidCheck,
        'startingPrice': startingPrice, 'lastFiveBid': lastFiveBid
    })


def createWatchList(request):
    if request.method == 'POST':
        addWatchlist = WatchList()
        addWatchlist.user = request.user
        itemId = request.POST.get('items_id')
        addWatchlist.items = ActiveListing.objects.get(id=itemId)

        # Check if the item and the username are in the watchlist database (same row)
        itemIsInList = WatchList.objects.filter(items=addWatchlist.items).filter(user=addWatchlist.user)
        # itemIsInList = WatchList.objects.filter(items=addWatchlist.items) & WatchList.objects.filter(user=addWatchlist.user)
        if itemIsInList.exists() == False:
            # Check if the user is logged in
            try:
                # If logged in, it'll save and add to the watchlist
                User.objects.get(username=addWatchlist.user)
                addWatchlist.save()
                return HttpResponseRedirect(reverse('item',args=[itemId]))
            except User.DoesNotExist:
                # If user is not logged in, it won't save it
                return HttpResponseRedirect(reverse('item',args=[itemId]))
        elif itemIsInList.exists():
            itemIsInList.delete()
            return HttpResponseRedirect(reverse('item',args=[itemId]))

    return HttpResponseRedirect(reverse("index"))


def watchlist(request):
    user = request.user
    msg = ''

    itemIsInWatchlist = WatchList.objects.filter(user=user)

    if itemIsInWatchlist.exists() == False:
        msg = 'Your watchlist is empty.'        

    return render(request, "auctions/watchlist.html", {
        'items': itemIsInWatchlist, 'msg': msg
    })


# List all categories
def categories(request):
    categories = ActiveListing.objects.all()

    # Store the categories in set(), thus it will keep just one instance of each category
    categoryList = set()
    for cat in categories:
        categoryList.add(cat.category)

    return render(request, "auctions/categories.html", {
        'categoryList': categoryList
    })


# Items within the specified category
def category(request, category):
    # Filter all items which belongs to the category
    category = ActiveListing.objects.filter(category=category).order_by('-id')
    
    # Store the category title in set(), thus it will keep just one instance of the title
    categoryTitleSet = set()
    for cat in category:
        categoryTitleSet.add(cat.category)

    # Set() converted to list and extract the title
    categoryTitle = list(categoryTitleSet)[0]

    return render(request, "auctions/categories.html", {
        'category': category, 'categoryTitle': categoryTitle
    })

# Add and save comments
def comment(request):
    if request.method == 'POST':
        if request.POST.get('comment'):
            # A small server side form validation only for the length of the inputs
            if len(request.POST.get('comment')) < 512:
                create = Comments()
                itemId = request.POST.get('item_id')
                create.user = request.user
                create.item = ActiveListing.objects.get(id=itemId)
                create.comment = request.POST.get('comment')
                create.save()

    return HttpResponseRedirect(reverse('item',args=[itemId]))


def bid(request):
    if request.method == 'POST':
        # Create a new bid
        if request.POST.get('bid'):
            # A small server side form validation only for the length of the inputs
            if len(request.POST.get('bid')) < 10:
                create = Bids()
                user = request.user
                itemId = request.POST.get('item_id')
                newBid = Decimal(request.POST.get('bid'))
                item = ActiveListing.objects.get(id=itemId)
                # Get the starting price
                price = ActiveListing.objects.filter(id=itemId).values('price')
                startingPrice = price[0]['price']
                # Get the highest bid
                getMaxBid = Bids.objects.filter(item_id=itemId).aggregate(Max('bid'))
                # Extract the highest bid
                maxBid = getMaxBid['bid__max']

                # If a bid already exist
                if Bids.objects.filter(item_id=itemId).exists():
                    # Check if the new bid is higher than the highest bid and the starting price, and if the item is active
                    if newBid > maxBid and newBid > startingPrice and item.active == True:
                        create.user = user
                        create.item = ActiveListing.objects.get(id=itemId)
                        create.bid = newBid
                        create.save()

                        return HttpResponseRedirect(reverse('item',args=[itemId]))
                # If a bid is not exist yet
                else:
                    # Check if bid is higher than the starting price, and if the item is active
                    if newBid > startingPrice and item.active == True:
                        create.user = user
                        create.item = ActiveListing.objects.get(id=itemId)
                        create.bid = newBid
                        create.save()
                    
                    return HttpResponseRedirect(reverse('item',args=[itemId]))
        
        # Close and Open a bid
        if request.POST.get('activate'):
            itemId = request.POST.get('item_id')
            item = ActiveListing.objects.get(id=itemId)
            
            if item.active == True:
                item.active = False
                item.save()

            elif item.active == False:
                item.active = True
                item.save()
            
            return HttpResponseRedirect(reverse('item',args=[itemId]))

    return HttpResponseRedirect(reverse('index'))
