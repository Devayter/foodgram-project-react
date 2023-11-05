from django_filters import rest_framework as filters

from .models import Recipe, Tag


class RecipeFilter(filters.FilterSet):

    tags = filters.MultipleChoiceFilter(
        field_name='tags__slug',
        choices=[(tag.slug, tag.slug) for tag in Tag.objects.all()],
        conjoined=False,
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags__slug',)
