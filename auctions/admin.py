from django.contrib import admin
from .models import User, ActiveListing, WatchList, Comments, Bids

class ActiveListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'shortDescription', 'description', 'price', 'category', 'active', 'image')


class WatchListAdmin(admin.ModelAdmin):
    list_display = ('user', 'items')

class CommentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'comment', 'created')

class BidAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'bid', 'created')


# Register your models here.
admin.site.register(User)
admin.site.register(ActiveListing, ActiveListingAdmin)
admin.site.register(WatchList, WatchListAdmin)
admin.site.register(Comments, CommentsAdmin)
admin.site.register(Bids, BidAdmin)