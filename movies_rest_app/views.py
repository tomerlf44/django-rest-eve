from django import shortcuts
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated

from movies_rest_app.models import *
from movies_rest_app.serializers import *
from auth.serializers import UserSerializer, SignupSerializer


# Create your views here.

# @api_view(['GET'])
# def get_movies(request):
#     query_set = Movie.objects.all()
#     movies_list = []
#     for movie in query_set:
#         movies_list.append({
#             'id': movie.pk,
#             'name': movie.name,
#             'description': movie.description
#         })
#     return Response(movies_list)


@api_view(['GET'])
def get_version(request):
    return Response({'version': 1.2})


@api_view(['GET', 'POST'])
def movies(request: Request):

    if request.method == 'GET':

        # get data from the DB
        movies_qs = Movie.objects.all()
        print(movies_qs.query)

        if 'name' in request.query_params:
            movies_qs = movies_qs.filter(name__iexact=request.query_params['name'])
            print(movies_qs.query)
        if 'duration_from' in request.query_params:
            movies_qs = movies_qs.filter(duration_in_min__gte=request.query_params['duration_from'])
            print(movies_qs.query)
        if 'duration_to' in request.query_params:
            movies_qs = movies_qs.filter(duration_in_min__lte=request.query_params['duration_to'])
            print(movies_qs.query)
        if 'description' in request.query_params:
            movies_qs = movies_qs.filter(description__icontains=request.query_params['description'])
            print(movies_qs.query)

        serializer = MovieSerializer(instance=movies_qs, many=True)
        return Response(serializer.data)

    else:
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=201)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def get_movie(request, movie_id):
    # try:
    #     movie = Movie.objects.get(id=movie_id)
    #     serializer = MovieDetailsSerializer(instance=movie, many=False)
    #     return Response(serializer.data)
    # except Movie.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'GET':
        serializer = MovieDetailsSerializer(instance=movie, many=False)
        return Response(serializer.data)
    elif request.method in ('PUT', 'PATCH'):
        serializer = MovieSerializer(instance=movie, data=request.data,
                                     partial=request.method == 'PATCH',
                                     context={'request': request})
        if serializer.is_valid(raise_exception=True):
            updated_movie = serializer.save()
            return Response(MovieDetailsSerializer(instance=updated_movie).data)
    else:
        movie.delete()
        return Response(status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def movie_actors(request: Request, movie_id):

    if request.method == 'GET':
        cast_qs = get_object_or_404(Movie, id=movie_id).movieactor_set.all()

        # apply filters
        if 'main_roles' in request.query_params \
                and request.query_params.get('main_roles').lower() == 'true':
            cast_qs = cast_qs.filter(main_role=True)
        if 'salary_from' in request.query_params:
            cast_qs = cast_qs.filter(salary__gte=request.query_params['salary_from'])
        if 'salary_to' in request.query_params:
            cast_qs = cast_qs.filter(salary__lte=request.query_params['salary_to'])

        # serializer = CastSerializer(instance=cast_qs, many=True)
        serializer = CastWithActorNameSerializer(instance=cast_qs, many=True)
        # serializer = AddCastSerializer(instance=cast_qs, many=True)
        return Response(serializer.data)
    else:
        get_object_or_404(Movie, id=movie_id)

        # Option 1
        # serializer = AddCastSerializer(data=request.data, context={'movie_id': movie_id})
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # return Response(serializer.data)

        # option 2
        # serializer = AddCastSerializer(data=request.data, context={'movie': movie})
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        # return Response(serializer.data)

        # option 3
        data = request.data.copy()
        data['movie'] = movie_id
        # serializer = AddCastSerializer(data=data)
        serializer = CastWithActorNameSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def me(request):
    if request.user.is_authenticated:
        s = UserSerializer(instance=request.user)
        return Response(data=s.data)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def signup(request):
    s = SignupSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    s.save()
    return Response(data=s.data)