from django.urls import path
from django.views.generic import RedirectView

from .course_views import (
    GlobalLectureCreateView,
    LectureCreateView,
    LectureDeleteView,
    LectureListView,
    LectureUpdateView,
    ModuleCreateView,
    ModuleDeleteView,
    ModuleDetailView,
    ModuleListView,
    ModuleUpdateView,
)
from .deadline_views import (
    DeadlineCreateView,
    DeadlineDeleteView,
    DeadlineListView,
    DeadlineStatusUpdateView,
    DeadlineUpdateView,
)
from .material_views import (
    MaterialSearchView,
    StudyMaterialCreateView,
    StudyMaterialDeleteView,
    StudyMaterialListView,
    StudyMaterialUpdateView,
)
from .plan_views import (
    StudyPlanEntryCreateView,
    StudyPlanEntryDeleteView,
    StudyPlanEntryListView,
    StudyPlanEntryStatusUpdateView,
    StudyPlanEntryUpdateView,
)
from .progress_views import ProgressView
from .task_views import (
    TaskCreateView,
    TaskDeleteView,
    TaskListView,
    TaskStatusUpdateView,
    TaskUpdateView,
)
from .views import CalendarDayView, CalendarWeekView, CalendarView, DashboardView, UserLoginView, UserLogoutView, UserRegisterView, DaVinciImportView
from .api_views import CalendarEventMoveAPIView, CalendarEventCopyAPIView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='dashboard', permanent=False), name='home'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('calendar/', CalendarView.as_view(), name='ui-calendar'),
    path('calendar/<int:year>/<int:month>/<int:day>/', CalendarDayView.as_view(), name='ui-calendar-day'),
    path('calendar/week/<int:year>/<int:month>/<int:day>/', CalendarWeekView.as_view(), name='ui-calendar-week'),
    path('modules/', ModuleListView.as_view(), name='ui-module-list'),
    path('modules/new/', ModuleCreateView.as_view(), name='ui-module-create'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='ui-module-detail'),
    path('modules/<int:pk>/edit/', ModuleUpdateView.as_view(), name='ui-module-update'),
    path('modules/<int:pk>/delete/', ModuleDeleteView.as_view(), name='ui-module-delete'),
    path(
        'modules/<int:module_id>/lectures/new/',
        LectureCreateView.as_view(),
        name='ui-lecture-create',
    ),
    path('lectures/new/', GlobalLectureCreateView.as_view(), name='ui-lecture-create-global'),
    path('lectures/', LectureListView.as_view(), name='ui-lecture-list'),
    path('lectures/<int:pk>/edit/', LectureUpdateView.as_view(), name='ui-lecture-update'),
    path('lectures/<int:pk>/delete/', LectureDeleteView.as_view(), name='ui-lecture-delete'),
    path('tasks/', TaskListView.as_view(), name='ui-task-list'),
    path('tasks/new/', TaskCreateView.as_view(), name='ui-task-create'),
    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='ui-task-update'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='ui-task-delete'),
    path('tasks/<int:pk>/status/', TaskStatusUpdateView.as_view(), name='ui-task-status'),
    path('deadlines/', DeadlineListView.as_view(), name='ui-deadline-list'),
    path('deadlines/new/', DeadlineCreateView.as_view(), name='ui-deadline-create'),
    path('deadlines/<int:pk>/edit/', DeadlineUpdateView.as_view(), name='ui-deadline-update'),
    path('deadlines/<int:pk>/delete/', DeadlineDeleteView.as_view(), name='ui-deadline-delete'),
    path('deadlines/<int:pk>/status/', DeadlineStatusUpdateView.as_view(), name='ui-deadline-status'),
    path('study-plans/', StudyPlanEntryListView.as_view(), name='ui-plan-list'),
    path('study-plans/new/', StudyPlanEntryCreateView.as_view(), name='ui-plan-create'),
    path('study-plans/<int:pk>/edit/', StudyPlanEntryUpdateView.as_view(), name='ui-plan-update'),
    path('study-plans/<int:pk>/delete/', StudyPlanEntryDeleteView.as_view(), name='ui-plan-delete'),
    path('study-plans/<int:pk>/status/', StudyPlanEntryStatusUpdateView.as_view(), name='ui-plan-status'),
    path('progress/', ProgressView.as_view(), name='ui-progress'),
    path('materials/', StudyMaterialListView.as_view(), name='ui-material-list'),
    path('materials/new/', StudyMaterialCreateView.as_view(), name='ui-material-create'),
    path('materials/<int:pk>/edit/', StudyMaterialUpdateView.as_view(), name='ui-material-update'),
    path('materials/<int:pk>/delete/', StudyMaterialDeleteView.as_view(), name='ui-material-delete'),
    path('search/', MaterialSearchView.as_view(), name='ui-search'),
    path('import-davinci/', DaVinciImportView.as_view(), name='ui-import-davinci'),
    path('api/event/move/', CalendarEventMoveAPIView.as_view(), name='ui-api-event-move'),
    path('api/event/copy/', CalendarEventCopyAPIView.as_view(), name='ui-api-event-copy'),
]
