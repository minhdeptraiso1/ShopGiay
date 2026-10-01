from django.contrib import admin

from .models import Banner, Review, Voucher, VoucherAllocation, VoucherUsage, WishlistItem

admin.site.register([Voucher, VoucherUsage, VoucherAllocation, WishlistItem, Review, Banner])
