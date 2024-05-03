
from django.urls import path
from authorizeapp import views
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name="home"),
    path('create_workout/', views.create_workout_view, name="create_workout"),
    path('add_exercise/', views.add_custom_exercise, name='add_custom_exercise'),
    path('my_workouts/', views.my_workout_view, name="my_workout"),
    path('my_workouts/copy/<int:workout_id>', views.copy_own_workout, name='copy_own_workout'),
    path('submit/', views.submit, name="submit"),
    path('my_workouts/edit/<int:workout_id>/', views.edit_workout, name='edit_workout'),
    path('my_workouts/delete/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    path('my_session/', views.my_sessions, name="my_session"),
    path('create_session/', views.create_session, name="create_session"),
    path('create_session/details/<int:session_id>/', views.add_details, name="add_details"),
    path('my_session/edit/<int:session_id>', views.edit_session, name="edit_session"),
    path('my_session/delete/<int:session_id>/', views.delete_session, name='delete_session'),
    path('food/', views.food_view, name="foods"),
    path('friends/', views.list_friends, name='list_friends'),
    path('add_friend/<int:user_id>/', views.add_friend, name='add_friend'),
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('friends/workouts/<int:user_id>/', views.view_friend_workout, name='view_friend_workout'),
    path('myprofile/', views.profile, name="myprofile"),
    path('myprofile/muscle_update', views.update_muscle, name="update_muscle"),
    path('myprofile/fat_update', views.update_fat, name="update_fat"),
    path('myprofile/weight_update', views.update_weight, name="update_weight"),
    path('myprofile/muscle_data/', views.get_muscle_data, name='muscle_data'),
    path('myprofile/fat_data/', views.get_fat_data, name='fat_data'),
    path('myprofile/weight_data/', views.get_weight_data, name='weight_data'),
    path('myprofile/bmi_data/', views.get_bmi_data, name='bmi_data'),
    path('myprofile/update', views.update_profile, name="update_profile"),
    path('myprofile/update_profile_picture/', views.update_profile_picture, name='update_profile_picture'),
    path('myprofile/PRs', views.exercise_progression_view, name="my_PRs"),
    path('myprofile/plot_progression', views.plot_progression, name='plot'),
    path('myprofile/settings', views.settings_view, name='settings'),
    path('friends/workouts/<int:user_id>/plot_progression_friend', views.plot_progression_friend, name='plot_friend'),
    path('myprofile/show_reps', views.show_reps, name='show_reps'),
    path('friends/workouts/<int:user_id>/show_reps', views.show_reps_friend, name='show_reps_friend'),
    path('friends/workouts/copy/<int:workout_id>', views.copy_workout, name='copy_workout'),
    path('friends/workouts/<int:user_id>/plot_prs', views.plot_prs_friend, name='plot_prs_friend'),
    path('myprofile/plot_prs', views.plot_prs, name='plot_prs'),
    path('add_pr/', views.add_pr, name='add_pr'),
    path('exercises/', views.exercises, name='exercises'),
    path('logout/', views.logout_view, name='logout'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)