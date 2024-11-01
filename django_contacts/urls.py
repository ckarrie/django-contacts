from django.urls import path
from . import views

urlpatterns = [
    path('carddav/<int:pk>/', views.CardDAVView.as_view(), name='carddav'),

    #path('.well-known/caldav',
    #     views.WellKnownView.as_view(type='caldav'), name='well-known-caldav'),
    #path('.well-known/carddav',
    #     views.WellKnownView.as_view(type='carddav'), name='well-known-carddav'),
]
