from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .fields import TheaterField
from .models import Actor, Genre, Movie, Showtime

# Register your models here.


class TheaterListFilter(admin.AllValuesFieldListFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_choices = settings.THEATERS

    def choices(self, changelist):
        add_facets = changelist.add_facets
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        yield {
            "selected": self.lookup_val is None and self.lookup_val_isnull is None,
            "query_string": changelist.get_query_string(
                remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]
            ),
            "display": _("All"),
        }
        include_none = False
        count = None
        empty_title = self.empty_value_display
        for i, theater in enumerate(self.lookup_choices):
            if add_facets:
                count = facet_counts[f"{i}__c"]
            if theater is None:
                include_none = True
                empty_title = f"{empty_title} ({count})" if add_facets else empty_title
                continue
            yield {
                "selected": self.lookup_val is not None and theater.id in self.lookup_val,
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: theater.id}, [self.lookup_kwarg_isnull]
                ),
                "display": f"{theater.name} ({count})" if add_facets else theater.name,
            }
        if include_none:
            yield {
                "selected": bool(self.lookup_val_isnull),
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg_isnull: "True"}, [self.lookup_kwarg]
                ),
                "display": empty_title,
            }


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")
    ordering = ("first_name", "last_name")
    readonly_fields = ("id",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("id",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "runtime_human", "want_to_see_count")
    search_fields = ("title", "genres", "cast", "director")
    list_filter = ("genres",)
    ordering = ("-want_to_see_count",)
    readonly_fields = ("id",)


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ("movie", "start_time", "theater_name")
    list_filter = ("start_time", ("theater_id", TheaterListFilter))
    search_fields = ("movie__title", "theater__name")
    readonly_fields = ("id",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Use TheaterField for the theater_id field
        if isinstance(db_field, TheaterField):
            return db_field.formfield(**kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = self.model.all_objects.get_queryset().select_related("movie")
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
