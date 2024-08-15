from django.contrib import admin
from .models import Movie, Genre, Comment, Watchlist
from django import forms


class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__' 
        

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ['user', 'comment', 'timestamp']
    readonly_fields = ['timestamp']



class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'tmdb_id', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class MovieAdmin(admin.ModelAdmin):
    form = MovieForm
    list_display = ('id', 'slug', 'title', 'release_date', 'language', 'display_genres', 'average_rating')
    list_filter = ('release_date', 'genres__name', 'language')
    search_fields = ('title', 'cast', 'slug')
    inlines = [CommentInline]
    readonly_fields = ('average_rating', 'slug')

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    display_genres.short_description = 'Genres'


class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'watched', 'added_on')
    list_filter = ('watched', 'added_on', 'user__email')
    search_fields = ('user__email', 'movie__title')
    date_hierarchy = 'added_on'




admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Comment)
admin.site.register(Watchlist, WatchlistAdmin)
