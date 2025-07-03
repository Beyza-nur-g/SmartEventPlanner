# events/urls.py - Güncellenmiş Hali
from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('create/', views.create_event, name='create_event'),
    path('update/<int:event_id>/', views.update_event, name='update_event'),
    path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('event/<int:event_id>/participate/', views.participate_event, name='participate_event'),
    
    path('event/<int:event_id>/add_message/', views.add_message, name='add_message'),
    path('my_events/', views.my_events, name='my_events'),
     path('myevents/<int:event_id>/', views.myevent_detail, name='myevent_detail'),
    path('myevents/<int:event_id>/remove/', views.remove_participation, name='remove_participationA'),
    path('recommend_events/', views.recommend_events, name='recommend_events'),


    path('recommend_events/interests/', views.recommend_events_by_interests, name='recommend_events_by_interests'),
    path('recommend_events/participation/', views.recommend_events_by_participation, name='recommend_events_by_participation'),
    path('recommend_events/location/', views.recommend_events_by_location, name='recommend_events_by_location'),
]

