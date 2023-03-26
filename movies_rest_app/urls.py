"""
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from movies_rest_app import views

urlpatterns = [
    path('movies', views.get_movies),
    path('movies/<int:movie_id>', views.get_movie),
    path('movies/<int:movie_id>/actors', views.get_movie_actors)
]

# api/imdb/movies/abc