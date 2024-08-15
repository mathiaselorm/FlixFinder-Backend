from django.contrib import admin
from .models import Rating

class RatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'score', 'created_at', 'updated_at')
    list_filter = ('movie', 'score', 'created_at', 'updated_at')
    search_fields = ('movie__title', 'user__email', 'score')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('movie', 'user', 'score')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

admin.site.register(Rating, RatingAdmin)
