from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from movies_rest_app.models import *


class ActorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actor
        exclude = ['birth_year']


class DetailedActorSerializer(serializers.ModelSerializer):

    model = ''
    class Meta:
        model = Actor
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):

    class Meta:
        model = Movie
        exclude = ['actors']
        extra_kwargs = {
            'id': {'read_only': True},
            'description': {'write_only': True, 'required': False}
        }

    # def validate(self, attrs):
    #     self.context['request']


class MovieDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        exclude = ['actors']


class CastSerializer(serializers.ModelSerializer):

    class Meta:
        model = MovieActor
        exclude = ['movie', 'id']
        depth = 1

# Option 1
class AddCastSerializer(serializers.Serializer):

    actor = serializers.PrimaryKeyRelatedField(queryset=Actor.objects.all())
    salary = serializers.IntegerField()
    main_role = serializers.BooleanField()


    def create(self, validated_data):
        return MovieActor.objects.create(movie_id=self.context['movie_id'], **validated_data)


# Option 2
# class AddCastSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = MovieActor
#         fields = ['actor', 'salary', 'main_role']
#
#
#     def create(self, validated_data):
#         validated_data['movie'] = self.context['movie']
#         return super().create(validated_data)


# # Option 3
# class AddCastSerializer(serializers.ModelSerializer):
#
#     # movie = serializers.PrimaryKeyRelatedField(queryset=Movie.objects.all(), write_only=True)
#
#     class Meta:
#         model = MovieActor
#         fields = ['actor', 'salary', 'main_role', 'movie']
#         extra_kwargs = {'movie': {'write_only': True}}


class AddCastSerializer(serializers.ModelSerializer):

    class Meta:
        model = MovieActor
        fields = ['actor', 'salary', 'main_role', 'movie']
        extra_kwargs = {'movie': {'write_only': True}}
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=MovieActor.objects.all(),
                fields=['movie', 'actor']
            )
        ]

    def validate_salary(self, value):
        if value > 100_000_000:
            raise serializers.ValidationError('Way too much money for the role')
        return value


class CastWithActorNameSerializer(serializers.ModelSerializer):

    actor = serializers.SlugRelatedField(slug_field='name', read_only=True)
    serializers.StringRelatedField
    # Relationships must either set a queryset explicitly, or set read_only=True.

    class Meta:
        model = MovieActor
        exclude = ['movie', 'id']


class ThinActor(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['name', 'id']


class MinimalActor(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id']


class ThinMovie(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['name', 'id']


class OscarSerializer(serializers.ModelSerializer):
    actor = ThinActor()
    movie = ThinMovie()

    class Meta:
        model = Oscar
        fields = '__all__'
        # extra_kwargs = {'movie': {'write_only': True}}

    # def create(self, validated_data):
    #     validated_data['movie'] = self.context['movie']
    #     return super().create(validated_data)


class PostOscarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Oscar
        # fields = ['actor', 'nomination_type', 'year', 'movie']
        fields = '__all__'
        # exclude = ['movie']
        # extra_kwargs = {'movie': {'write_only': True}}

    def validate(self, attrs):
        if attrs.get("actor"):
            if attrs.get("nomination_type") in ["best actor", "sababa actor"]:
                return attrs
            else:
                raise serializers.ValidationError("error. passing actor for only movie nomination award")
        else:
            return attrs


class OscarUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Oscar
        fields = '__all__'

    def validate(self, attrs):
        fields_list = [field for field in attrs if field not in ['actor', 'movie']]
        if fields_list:
            raise serializers.ValidationError("error. cant modify fields other than actor or movie")
        return attrs