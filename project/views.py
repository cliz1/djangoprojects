# File: views.py
# Author: Nathaniel Clizbe (clizbe@bu.edu), 12/10/2024
# Description: Views for final project (so a user can view things)

from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.db.models import Case, When, Value, CharField
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, UpdateView
from django.db.models import Count, Q, Sum, F, FloatField
from .models import Student, Parent, TutoringService, AdvocacyService
from datetime import timedelta, date, datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from .forms import ParentSearchForm, StudentUpdateForm, StudentSearchForm, ParentUpdateForm, StudentForm, ParentForm, ChartsFilterForm
import plotly.express as px


# Create your views here.

class HomePageView(LoginRequiredMixin, TemplateView):
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

        context["parents_by_country"] = (
            Parent.objects.values("country_of_origin")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

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

        # New statistic: Total service hours
        tutoring_hours = TutoringService.objects.aggregate(total_hours=Sum('length_of_session'))['total_hours'] or 0
        advocacy_hours = AdvocacyService.objects.aggregate(total_hours=Sum('length_of_contact'))['total_hours'] or 0
        context['tutoring_hours'] = tutoring_hours
        context['advocacy_hours'] = advocacy_hours

        return context

class StudentSearchView(LoginRequiredMixin, ListView):
    model = Student
    template_name = "project/student_search.html"
    context_object_name = "students"
    paginate_by = 10

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
    

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'project/student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the related tutoring and advocacy service logs
        student = self.get_object()
        context['tutoring_sessions'] = student.tutoring_sessions.all().order_by('-date_of_contact')
        context['advocacy_sessions'] = student.advocacy_sessions.all().order_by('-date_of_contact')

        # Calculate total tutoring and advocacy hours for the student
        tutoring_hours = TutoringService.objects.filter(student=student).aggregate(total_hours=Sum('length_of_session'))['total_hours'] or 0
        advocacy_hours = AdvocacyService.objects.filter(student=student).aggregate(total_hours=Sum('length_of_contact'))['total_hours'] or 0
        
        # Add to context
        context['tutoring_hours'] = tutoring_hours
        context['advocacy_hours'] = advocacy_hours
        context['total_hours'] = tutoring_hours + advocacy_hours

        return context

class ParentSearchView(LoginRequiredMixin, ListView):
    model = Parent
    template_name = "project/parent_search.html"
    context_object_name = "parents"
    paginate_by = 10 

    def get_queryset(self):
        queryset = Parent.objects.all()

        # Get search and filter parameters from GET request
        search_name = self.request.GET.get("search_name", "")
        town_filter = self.request.GET.get("town_village", "")

        # Apply search by name (case-insensitive)
        if search_name:
            name_parts = search_name.split()  # Splitting input into parts
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
   

class ParentDetailView(LoginRequiredMixin, DetailView):
    model = Parent
    template_name = 'project/parent_detail.html'
    context_object_name = 'parent'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parent = self.get_object()

        # Add the list of students (kids) of the parent to the context
        context['students'] = Student.objects.filter(parent=parent)
        return context

class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = 'project/student_update.html'

    def get_success_url(self):
        # Redirect to the student's detail page after a successful update
        return reverse_lazy('student_detail', kwargs={'pk': self.object.pk})
    

class ParentUpdateView(LoginRequiredMixin, UpdateView):
    model = Parent
    form_class = ParentUpdateForm
    template_name = 'project/parent_update.html'

    def get_success_url(self):
        # Redirect to the student's detail page after a successful update
        return reverse_lazy('parent_detail', kwargs={'pk': self.object.pk})

class IntakeView(LoginRequiredMixin, View):
    def get(self, request):
        parent_form = ParentForm()
        student_form = StudentForm()
        return render(request, 'project/intake.html', {'parent_form': parent_form, 'student_form': student_form})

    def post(self, request):
        parent_form = ParentForm(request.POST)
        student_form = StudentForm(request.POST)

        if 'add_parent' in request.POST and parent_form.is_valid():
            parent_form.save()
            return redirect('intake')  # Redirect back to intake page after saving parent

        if 'add_student' in request.POST and student_form.is_valid():
            student_form.save()
            return redirect('intake')  # Redirect back to intake page after saving student

        return render(request, 'intake.html', {'parent_form': parent_form, 'student_form': student_form})

class DeleteServiceView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Find the service by primary key
        service = get_object_or_404(TutoringService, pk=pk)  
        # Delete the service
        service.delete()
        # Redirect back to the student's detail page
        return redirect('student_detail', pk=service.student.pk)

class DeleteAdvocacyServiceView(LoginRequiredMixin, View):
    def post(self, request, pk):
        # Find the service by primary key
        service = get_object_or_404(AdvocacyService, pk=pk)  
        # Delete the service
        service.delete()
        # Redirect back to the student's detail page
        return redirect('student_detail', pk=service.student.pk)

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

def charts_view(request):
    form = ChartsFilterForm(request.GET or None)
    town_filter = request.GET.getlist('town_village')
    level_filter = request.GET.getlist('school_level')
    time_filter = request.GET.get('time_range', 'all')



    # Determine the time range
    today = date.today()
    if time_filter == '2weeks':
        start_date = today - timedelta(weeks=2)
    elif time_filter == '6months':
        start_date = today - timedelta(days=6*30)
    elif time_filter == '1year':
        start_date = today - timedelta(days=365)
    else:
        start_date = datetime(1970, 1, 1)

    # Annotate school levels dynamically
    students = Student.objects.annotate(
        school_level=Case(
            When(current_grade__gte=9, then=Value('High School')),
            When(current_grade__lt=9, current_grade__gte=4, then=Value('Middle School')),
            When(current_grade__lt=4, then=Value('Elementary')),
            default=Value('Unknown'),
            output_field=CharField()
        )
    )

    # Apply filters
    if town_filter:
        students = students.filter(town_village__in=town_filter)
    if level_filter:
        students = students.filter(school_level__in=level_filter)

    # Filter services by time range
    tutoring_sessions = students.prefetch_related('tutoring_sessions')
    advocacy_sessions = students.prefetch_related('advocacy_sessions')
    if start_date:
        tutoring_sessions = tutoring_sessions.filter(tutoring_sessions__date_of_contact__gte=start_date)
        advocacy_sessions = advocacy_sessions.filter(advocacy_sessions__date_of_contact__gte=start_date)

    # 1. Service Hours by Town/Village (Bar Graph)
    service_data = students.annotate(
        total_service_hours=Sum(
            Case(
                When(tutoring_sessions__date_of_contact__gte=start_date, then=F('tutoring_sessions__length_of_session')),
                When(advocacy_sessions__date_of_contact__gte=start_date, then=F('advocacy_sessions__length_of_contact')),
                default=0,
                output_field=FloatField(),
            )
        )
    ).values('town_village', 'total_service_hours').order_by('town_village')

    town_villages = [entry['town_village'] for entry in service_data]
    service_hours = [entry['total_service_hours'] for entry in service_data]

    fig1 = px.bar(
        x=town_villages,
        y=service_hours,
        labels={'x': 'District', 'y': 'Service Hours'},
        title='Service Hours by School District'
    )

    # 2. Service Hours by School Level (Pie Chart)
    level_data = students.annotate(
        total_service_hours=Sum(
            Case(
                When(tutoring_sessions__date_of_contact__gte=start_date, then=F('tutoring_sessions__length_of_session')),
                When(advocacy_sessions__date_of_contact__gte=start_date, then=F('advocacy_sessions__length_of_contact')),
                default=0,
                output_field=FloatField(),
            )
        )
    ).values('school_level', 'total_service_hours')

    levels = [entry['school_level'] for entry in level_data]
    level_hours = [entry['total_service_hours'] for entry in level_data]

    fig2 = px.pie(
        names=levels,
        values=level_hours,
        title='Service Hours by School Level'
    )

    # 3. Clients by Country of Origin (Pie Chart)
    client_data = students.filter(
        Q(tutoring_sessions__date_of_contact__gte=start_date) | Q(advocacy_sessions__date_of_contact__gte=start_date)
    ).distinct().values('country_of_origin').annotate(count=Count('id', distinct=True))

    client_countries = [entry['country_of_origin'] for entry in client_data]
    client_counts = [entry['count'] for entry in client_data]

    fig3 = px.pie(
        names=client_countries,
        values=client_counts,
        title='Clients by Country of Origin'
    )

    # 4. Parents by Country of Origin (Pie Chart)
    parent_ids = students.filter(
        Q(tutoring_sessions__date_of_contact__gte=start_date) | Q(advocacy_sessions__date_of_contact__gte=start_date)
    ).distinct().values_list('parent_id', flat=True)

    parent_data = Parent.objects.filter(id__in=parent_ids).values('country_of_origin').annotate(count=Count('id'))

    parent_countries = [entry['country_of_origin'] for entry in parent_data]
    parent_counts = [entry['count'] for entry in parent_data]

    fig4 = px.pie(
        names=parent_countries,
        values=parent_counts,
        title='Parents by Country of Origin'
    )

    # Convert plots to HTML
    context = {
        'form': form,
        'graph1_html': fig1.to_html(full_html=False),
        'graph2_html': fig2.to_html(full_html=False),
        'graph3_html': fig3.to_html(full_html=False),
        'graph4_html': fig4.to_html(full_html=False),
    }
    return render(request, 'project/charts.html', context)