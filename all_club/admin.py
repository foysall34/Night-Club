from django.contrib import admin

# Register your models here.
from .models import Club

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ( 'id' ,  'name', )
    search_fields = ('name', 'city', 'state', 'categories')
    list_filter = ('city', 'state', 'is_nightlife', 'price_level')
