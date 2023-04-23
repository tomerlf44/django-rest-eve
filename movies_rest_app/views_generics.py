import django_filters
from django_filters import FilterSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from django.db.models import Count
from django.shortcuts import get_object_or_404

from movies_rest_app.models import Movie
from movies_rest_app.serializers import *


# api/imdb/movies - GET POST
# api/imdb/movies/movie_id - GET UPDATE DELETE


class MovieFilterSet(FilterSet):

    name = django_filters.CharFilter(field_name='name', lookup_expr='iexact')
    duration_from = django_filters.NumberFilter('duration_in_min', lookup_expr='gte')

    class Meta:
        model = Movie
        fields = ['name']


class MoviesViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    # filter_backends = [DjangoFilterBackend]
    filterset_class = MovieFilterSet
    # pagination_class = PageNumberPagination


    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MovieDetailsSerializer
        else:
            return super().get_serializer_class()


    # movies/movie_id/actors
    # movies/actors
    @action(methods=['GET'], detail=True, url_path='actors')
    def movie_actors(self, request, pk):
        cast_qs = self.get_object().movieactor_set.all()
        serializer = CastWithActorNameSerializer(instance=cast_qs, many=True)
        return Response(data=serializer.data)


class OscarViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    queryset = Oscar.objects.all()
    serializer_class = OscarSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return PostOscarSerializer
        if self.action == 'update':
            return OscarUpdateSerializer
        else:
            return super().get_serializer_class()


    # def update(self, request, *args, **kwargs):
    #     partial = True
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # forcibly invalidate the prefetch cache on the instance.
    #         instance._prefetched_objects_cache = {}
    #
    #     return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        if self.action == "update":
            kwargs['partial'] = True
        return serializer_class(*args, **kwargs)


    @action(methods=['GET'], detail=False, url_path='years')
    def oscars_by_year(self, request, pk):
        # need to extract id of year by accessing the full url attr
        print('smth')
        pass

    @action(methods=['GET'], detail=False, url_path='most-oscars-awarded-movie')
    def oscars_by_year(self, request):
        top_movie = Oscar.objects.values('movie').annotate(oscars_count=Count('id')).order_by('-oscars_count'
                ).first()['movie']
        obj = get_object_or_404(Movie, id=top_movie)
        serializer = ThinMovie(instance=obj, many=False)
        return Response(status=200, data=serializer.data)


    @action(methods=['GET'], detail=False, url_path='total-oscars')
    def oscars_by_year(self, request):
        total_oscars = Oscar.objects.aggregate(total_count=Count('id'))['total_count']
        return Response(status=200, data=total_oscars)