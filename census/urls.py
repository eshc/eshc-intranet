from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required
from users.decorators import current_member_required, check_role

app_name = 'census'

urlpatterns = [
    path('census/<int:session_id>/', login_required(current_member_required(views.CensusView.as_view())), name='census-form'),
    path('census_results/<int:session_id>/', login_required(check_role(views.CensusResultsView.as_view(), "census_role")), name='census-results'),
]
