# File: views.py
# Author: Nathaniel Clizbe (clizbe@bu.edu), 12/10/2024
# Description: Views for final project (so a user can view things)

from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.db.models import Case, When, Value, CharField
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, DeleteView
from django.db.models import Count, Q, Sum, F, FloatField
from .models import Student, Parent, TutoringService, AdvocacyService
from datetime import timedelta, date, datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.timezone import now
from .forms import ParentSearchForm, StudentUpdateForm, StudentSearchForm, ParentUpdateForm, StudentForm, ParentForm, ChartsFilterForm
import plotly.express as px
from collections import Counter
import re


# Create your views here.

GRADE_LABELS = {
    -1: "OS",
    0: "K",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "11",
    12: "12",
    13: "13"
    # ... etc., or use str(x) as default
}


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

        grade_counts = (
        Student.objects.values("current_grade")
        .annotate(count=Count("id"))
        .order_by("current_grade")
        )

        # Map internal int grades to readable labels
        context["students_by_grade"] = [
            {
                "grade": GRADE_LABELS.get(entry["current_grade"], str(entry["current_grade"])),
                "count": entry["count"]
            }
            for entry in grade_counts
]

        context["parents_by_town"] = (Parent.objects.values('town_village').annotate(count=Count('id')))

        context["parents_by_country"] = (
            Parent.objects.values("country_of_origin")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        ## STUFF FOR TIME FILTERING
        thirty_days_ago = today - timedelta(days=30)
        six_months_ago = today - timedelta(days=6*30)  # Approx. 6 months
        one_year_ago = today - timedelta(days=365)

        # Students who received any service in the time range
        context["students_in_last_thirty_days"] = Student.objects.filter(
            Q(tutoring_sessions__date_of_contact__gte=thirty_days_ago) |
            Q(advocacy_sessions__date_of_contact__gte=thirty_days_ago)
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
    paginate_by = 50

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
        country_filter = self.request.GET.get("country_of_origin", "")

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

        #Apply filter for country of origin
        if country_filter:
            queryset = queryset.filter(country_of_origin=country_filter)

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

        print(parent_form.is_valid())
        print(parent_form.errors)
        if 'add_parent' in request.POST and parent_form.is_valid():
            parent_form.save()
            return redirect('intake')  # Redirect back to intake page after saving parent

        if 'add_student' in request.POST and student_form.is_valid():
            student_form.save()
            return redirect('intake')  # Redirect back to intake page after saving student

        return render(request, 'project/intake.html', {'parent_form': parent_form, 'student_form': student_form})
    
class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = "project/student_confirm_delete.html"
    success_url = reverse_lazy("home")  
    # replace "student-list" with the name of the view/URL where you list students

class ParentDeleteView(LoginRequiredMixin, DeleteView):
    model = Parent
    template_name = "project/parent_confirm_delete.html"
    success_url = reverse_lazy("home")  
    # similarly adjust to your parent-list view name

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
    selected_chart = request.GET.get('chart_type', 'service_by_town')


    # Determine the time range
    today = date.today()
    if time_filter == '30days':
        start_date = today - timedelta(days=30)
        time_title = " - Over the Last 30 Days"
    elif time_filter == '6months':
        start_date = today - timedelta(days=6*30)
        time_title = " - Over the Last 6 Months"
    elif time_filter == '1year':
        start_date = today - timedelta(days=365)
        time_title = " - Over the Last 1 year"
    else:
        start_date = datetime(1970, 1, 1)
        time_title = ""

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
    # For Tutoring/Advocacy Service Objects
    tutoring_data = TutoringService.objects.filter(student__in=students)
    advocacy_data = AdvocacyService.objects.filter(student__in=students)
    #Apply time filter to service data
    if start_date:
        tutoring_sessions = tutoring_sessions.filter(tutoring_sessions__date_of_contact__gte=start_date)
        advocacy_sessions = advocacy_sessions.filter(advocacy_sessions__date_of_contact__gte=start_date)
        tutoring_data = tutoring_data.filter(date_of_contact__gte=start_date)
        advocacy_data = advocacy_data.filter(date_of_contact__gte=start_date)


    # 1. Service Hours by Town/Village (Bar Graph)
    if selected_chart == 'service_by_town':
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
            title='Service Hours by School District' + time_title
        )
        chart_html = fig1.to_html(full_html=False)

    # 2. Service Hours by School Level (Pie Chart)
    elif selected_chart == 'service_by_level':
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
            title='Service Hours by School Level' + time_title
        )
        chart_html = fig2.to_html(full_html=False)

    # 3. Clients by Country of Origin (Pie Chart)
    elif selected_chart == 'clients_by_country':
        client_data = students.filter(
            Q(tutoring_sessions__date_of_contact__gte=start_date) | Q(advocacy_sessions__date_of_contact__gte=start_date)
        ).distinct().values('country_of_origin').annotate(count=Count('id', distinct=True))

        client_countries = [entry['country_of_origin'] for entry in client_data]
        client_counts = [entry['count'] for entry in client_data]

        fig3 = px.pie(
            names=client_countries,
            values=client_counts,
            title='Clients by Country of Origin' + time_title
        )
        chart_html = fig3.to_html(full_html=False)

    # 4. Parents by Country of Origin (Pie Chart)
    elif selected_chart == 'parents_by_country':
        parent_ids = students.filter(
            Q(tutoring_sessions__date_of_contact__gte=start_date) | Q(advocacy_sessions__date_of_contact__gte=start_date)
        ).distinct().values_list('parent_id', flat=True)

        parent_data = Parent.objects.filter(id__in=parent_ids).values('country_of_origin').annotate(count=Count('id'))

        parent_countries = [entry['country_of_origin'] for entry in parent_data]
        parent_counts = [entry['count'] for entry in parent_data]

        fig4 = px.pie(
            names=parent_countries,
            values=parent_counts,
            title='Parents by Country of Origin' + time_title
        )
        chart_html = fig4.to_html(full_html=False)

    # 5. Number of tutoring sessions by SUBJECT
    elif selected_chart == 'sessions_by_subject':
        raw_subjects = tutoring_data.values_list('session_focus', flat=True)

        subject_counter = Counter()
        for entry in raw_subjects:
            if entry:
                subjects = re.split(r'[/,]\s*', entry)
                cleaned = [s.strip().capitalize() for s in subjects if s.strip()]
                subject_counter.update(cleaned)

        session_subjects = list(subject_counter.keys())
        subject_counts = list(subject_counter.values())

        fig5 = px.bar(
            x=session_subjects,
            y=subject_counts,
            labels={'x': 'Subject', 'y': 'Number of Tutoring Sessions'},
            title='Number of Tutoring Sessions by Subject' + time_title
        )
        chart_html = fig5.to_html(full_html=False)

    # 6. Number of tutoring sessions by school district
    elif selected_chart == 'tutoring_sessions_by_district':
        tutoring_data = students.annotate(
        tutoring_session_count=Count(
            'tutoring_sessions',
            filter=Q(tutoring_sessions__date_of_contact__gte=start_date)
        )
        ).values('town_village', 'tutoring_session_count').order_by('town_village')
       
        town_villages = [entry['town_village'] for entry in tutoring_data]
        tutoring_session_count = [entry['tutoring_session_count'] for entry in tutoring_data]

        fig6 = px.bar(
            x=town_villages,
            y=tutoring_session_count,
            labels={'x': 'District', 'y': 'Tutoring Sessions'},
            title='Tutoring Sessions by School District' + time_title
        )
        chart_html = fig6.to_html(full_html=False)

    # 7. Number of advocacy sessions by school district
    elif selected_chart == 'advocacy_sessions_by_district':
        advocacy_data = students.annotate(
        advocacy_session_count=Count(
            'advocacy_sessions',
            filter=Q(advocacy_sessions__date_of_contact__gte=start_date)
        )
        ).values('town_village', 'advocacy_session_count').order_by('town_village')
       
        town_villages = [entry['town_village'] for entry in advocacy_data]
        advocacy_session_count = [entry['advocacy_session_count'] for entry in advocacy_data]

        fig7 = px.bar(
            x=town_villages,
            y=advocacy_session_count,
            labels={'x': 'District', 'y': 'Advocacy Sessions'},
            title='Advocacy Sessions by School District' + time_title
        )
        chart_html = fig7.to_html(full_html=False)


    # 8. Number of students by interval of number of hours served
    elif selected_chart == 'students_by_service_interval':
        students_with_hours = Student.objects.annotate(
        total_hours=Sum(
            Case(
                When(tutoring_sessions__date_of_contact__gte=start_date, then=F('tutoring_sessions__length_of_session')),
                When(advocacy_sessions__date_of_contact__gte=start_date, then=F('advocacy_sessions__length_of_contact')),
                default=0,
                output_field=FloatField()
            )
        )
        )
        binned_data = students_with_hours.aggregate(
        under_5=Count('id', filter=Q(total_hours__lt=5)),
        between_5_10=Count('id', filter=Q(total_hours__gte=5, total_hours__lt=10)),
        between_10_20=Count('id', filter=Q(total_hours__gte=10, total_hours__lt=20)),
        over_20=Count('id', filter=Q(total_hours__gte=20)))

        chart_data = [
            {'range': '0–5 hrs', 'count': binned_data['under_5']},
            {'range': '5–10 hrs', 'count': binned_data['between_5_10']},
            {'range': '10–20 hrs', 'count': binned_data['between_10_20']},
            {'range': '20+ hrs', 'count': binned_data['over_20']},
        ]

        # Create bar chart
        fig8 = px.bar(
            chart_data,
            x='range',
            y='count',
            title='Number of Students by Total Hours Served' + time_title,
            labels={'range': 'Hours Served', 'count': 'Number of Students'}
        )

        chart_html = fig8.to_html(full_html=False)

    # Convert plots to HTML
    context = {
        'form': form,
        'selected_chart': selected_chart,
        'chart_html': chart_html,
    }
    return render(request, 'project/charts.html', context)