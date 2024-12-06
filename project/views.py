from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, UpdateView
from django.db.models import Count, Q
from .models import Student, Parent, TutoringService, AdvocacyService
from datetime import timedelta
from django.utils.timezone import now
from .forms import ParentSearchForm, StudentUpdateForm, StudentSearchForm, ParentUpdateForm


# Create your views here.

class HomePageView(TemplateView):
    template_name = "project/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = now().date()

        # Statistics: Number of students grouped by various fields
        context["students_by_town"] = (
            Student.objects.values("town_village")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        context["students_by_country"] = (
            Student.objects.values("country_of_origin")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        context["students_by_grade"] = (
            Student.objects.values("current_grade")
            .annotate(count=Count("id"))
            .order_by("current_grade")
        )

        context["parents_by_town"] = (Parent.objects.values('town_village').annotate(count=Count('id')))

        ## STUFF FOR TIME FILTERING
        two_weeks_ago = today - timedelta(weeks=2)
        six_months_ago = today - timedelta(days=6*30)  # Approx. 6 months
        one_year_ago = today - timedelta(days=365)

        # Students who received any service in the time range
        context["students_in_last_two_weeks"] = Student.objects.filter(
            Q(tutoring_sessions__date_of_contact__gte=two_weeks_ago) |
            Q(advocacy_sessions__date_of_contact__gte=two_weeks_ago)
        ).distinct().count()

        context["students_in_last_six_months"] = Student.objects.filter(
            Q(tutoring_sessions__date_of_contact__gte=six_months_ago) |
            Q(advocacy_sessions__date_of_contact__gte=six_months_ago)
        ).distinct().count()

        context["students_in_last_year"] = Student.objects.filter(
            Q(tutoring_sessions__date_of_contact__gte=one_year_ago) |
            Q(advocacy_sessions__date_of_contact__gte=one_year_ago)
        ).distinct().count()

        return context

class StudentSearchView(ListView):
    model = Student
    template_name = "project/student_search.html"
    context_object_name = "students"
    paginate_by = 10  # Limit the number of results per page (optional)

    def get_queryset(self):
        queryset = Student.objects.all()

        # Get search and filter parameters from GET request
        search_name = self.request.GET.get("search_name", "")
        town_filter = self.request.GET.get("town_village", "")
        country_filter = self.request.GET.get("country_of_origin", "")
        grade_filter = self.request.GET.get("current_grade", "")
        #district_filter = self.request.GET.get("school_district", "")
        time_period = self.request.GET.get("time_period", "")

        # Apply search by name (case-insensitive)
        if search_name:
            name_parts = search_name.split()  # Split input into parts
            if len(name_parts) == 1:
                queryset = queryset.filter(
                Q(first_name__icontains=search_name) | Q(last_name__icontains=search_name)
            )
            elif len(name_parts) > 1:
                print("hit it")
                queryset = queryset.filter(
                Q(first_name__icontains=name_parts[0]) & Q(last_name__icontains=" ".join(name_parts[1:]))
        )

        # Apply filters for town, country, grade, and school district
        if town_filter:
            queryset = queryset.filter(town_village=town_filter)
        if country_filter:
            queryset = queryset.filter(country_of_origin=country_filter)
        if grade_filter:
            queryset = queryset.filter(current_grade=grade_filter)

        # Time filters
        # Time period filter
        if time_period:
            today = now().date()
            if time_period == '2_weeks':
                cutoff_date = today - timedelta(weeks=2)
            elif time_period == '6_months':
                cutoff_date = today - timedelta(weeks=26)
            elif time_period == '1_year':
                cutoff_date = today - timedelta(weeks=52)
            else:
                cutoff_date = None
            
            if cutoff_date:
                queryset = queryset.filter(
                    Q(tutoring_sessions__date_of_contact__gte=cutoff_date) |
                    Q(advocacy_sessions__date_of_contact__gte=cutoff_date)
                ).distinct()
    

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = StudentSearchForm(self.request.GET)
        return context
    

class StudentDetailView(DetailView):
    model = Student
    template_name = 'project/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the related tutoring and advocacy service logs
        student = self.get_object()
        context['tutoring_sessions'] = student.tutoring_sessions.all()
        context['advocacy_sessions'] = student.advocacy_sessions.all()

        return context

class ParentSearchView(ListView):
    model = Parent
    template_name = "project/parent_search.html"
    context_object_name = "parents"
    paginate_by = 10  # Limit the number of results per page (optional)

    def get_queryset(self):
        queryset = Parent.objects.all()

        # Get search and filter parameters from GET request
        search_name = self.request.GET.get("search_name", "")
        town_filter = self.request.GET.get("town_village", "")

        # Apply search by name (case-insensitive)
        if search_name:
            name_parts = search_name.split()  # Split input into parts
            if len(name_parts) == 1:
                queryset = queryset.filter(
                Q(first_name__icontains=search_name) | Q(last_name__icontains=search_name)
            )
            elif len(name_parts) > 1:
                print("hit it")
                queryset = queryset.filter(
                Q(first_name__icontains=name_parts[0]) & Q(last_name__icontains=" ".join(name_parts[1:]))
        )

        # Apply filter for town/village
        if town_filter:
            queryset = queryset.filter(town_village=town_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ParentSearchForm(self.request.GET)
        return context
   

class ParentDetailView(DetailView):
    model = Parent
    template_name = 'project/parent_detail.html'
    context_object_name = 'parent'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent = self.get_object()

        # Add the list of students (kids) of the parent to the context
        context['students'] = Student.objects.filter(parent=parent)
        return context

class StudentUpdateView(UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = 'project/student_update.html'

    def get_success_url(self):
        # Redirect to the student's detail page after a successful update
        return reverse_lazy('student_detail', kwargs={'pk': self.object.pk})
    

class ParentUpdateView(UpdateView):
    model = Parent
    form_class = ParentUpdateForm
    template_name = 'project/parent_update.html'

    def get_success_url(self):
        # Redirect to the student's detail page after a successful update
        return reverse_lazy('parent_detail', kwargs={'pk': self.object.pk})

@csrf_protect
def add_tutoring_service(request, pk):
    if request.method == 'POST':
        student = get_object_or_404(Student, pk=pk)
        TutoringService.objects.create(
            student=student,
            date_of_contact=request.POST['date_of_contact'],
            location_of_contact=request.POST['location_of_contact'],
            session_focus=request.POST['session_focus'],
            activity=request.POST['activity'],
            length_of_session=request.POST['length_of_session'],
        )
    return redirect('student_detail', pk=pk)

@csrf_protect
def add_advocacy_service(request, pk):
    if request.method == 'POST':
        student = get_object_or_404(Student, pk=pk)
        AdvocacyService.objects.create(
            student=student,
            date_of_contact=request.POST['date_of_contact'],
            school_district=request.POST['school_district'],
            description=request.POST['description'],
            length_of_contact=request.POST['length_of_contact'],
        )
    return redirect('student_detail', pk=pk)