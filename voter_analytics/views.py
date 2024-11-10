from django.shortcuts import render
from django.views.generic import ListView
from .models import Voter
from .forms import VoterFilterForm
from django.db.models import Q
from django.views.generic import DetailView
import plotly.express as px
from django.db.models import Count


class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'  # Custom template name
    context_object_name = 'voters'
    paginate_by = 100  # Display 100 voters per page

    def get_queryset(self):
        queryset = Voter.objects.all()
        form = VoterFilterForm(self.request.GET)

        if form.is_valid():
            # Filter by party affiliation 
            if form.cleaned_data['party_affiliation']:
                queryset = queryset.filter(party_affiliation=form.cleaned_data['party_affiliation'])

            # Filter by date of birth range
            min_dob = form.cleaned_data['min_date_of_birth']
            max_dob = form.cleaned_data['max_date_of_birth']
            if min_dob:
                queryset = queryset.filter(date_of_birth__year__gte=min_dob)
            if max_dob:
                queryset = queryset.filter(date_of_birth__year__lte=max_dob)

            # Filter by voter score
            if form.cleaned_data['voter_score']:
                queryset = queryset.filter(voter_score=form.cleaned_data['voter_score'])
            

             # Filter by election participation (corrected)
            elections = form.cleaned_data['elections']
            if elections:
                q_objects = Q()
                for election in elections:
                    # Dynamically create Q object for each election
                    q_objects &= Q(**{election: True}) 
                queryset = queryset.filter(q_objects)  

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VoterFilterForm(self.request.GET) 
        return context

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'


class VoterGraphsView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'
    
    def get_context_data(self, **kwargs):
        # Get the current context
        context = super().get_context_data(**kwargs)

        # Get the filter form from the GET request
        form = VoterFilterForm(self.request.GET)
        context['form'] = form

        # Start with all voters 
        voters = Voter.objects.all()

        # Apply filters based on form data
        if form.is_valid():
            # Filter by party affiliation
            if form.cleaned_data['party_affiliation']:
                voters = voters.filter(party_affiliation=form.cleaned_data['party_affiliation'])

            # Filter by minimum date of birth
            if form.cleaned_data['min_date_of_birth']:
                min_year = form.cleaned_data['min_date_of_birth']
                voters = voters.filter(date_of_birth__year__gte=min_year)

            # Filter by maximum date of birth
            if form.cleaned_data['max_date_of_birth']:
                max_year = form.cleaned_data['max_date_of_birth']
                voters = voters.filter(date_of_birth__year__lte=max_year)

            # Filter by voter score
            if form.cleaned_data['voter_score']:
                voters = voters.filter(voter_score=form.cleaned_data['voter_score'])

            # Filter by election participation
            elections = form.cleaned_data['elections']
            if elections:
                # Construct the filter based on selected elections
                filters = {election: True for election in elections}
                voters = voters.filter(**filters)

        # 1. Histogram: Distribution of Voters by Year of Birth
        birth_years = voters.values('date_of_birth__year').annotate(count=Count('id')).order_by('date_of_birth__year')
        birth_data = [{'year': b['date_of_birth__year'], 'count': b['count']} for b in birth_years]
        fig1 = px.bar(birth_data, x='year', y='count', title="Distribution of Voters by Year of Birth")
        context['birth_year_graph'] = fig1.to_html(full_html=False)

        # 2. Pie Chart: Distribution by Party Affiliation
        party_counts = voters.values('party_affiliation').annotate(count=Count('id'))
        party_data = [{'party_affiliation': p['party_affiliation'], 'count': p['count']} for p in party_counts]
        fig2 = px.pie(party_data, names='party_affiliation', values='count', title="Distribution of Voters by Party Affiliation")
        context['party_affiliation_graph'] = fig2.to_html(full_html=False)

        # 3. Histogram: Voters' Participation in Elections
        elections = {
            '2020 State Election': voters.filter(v20state=True).count(),
            '2021 Town Election': voters.filter(v21town=True).count(),
            '2021 Primary Election': voters.filter(v21primary=True).count(),
            '2022 General Election': voters.filter(v22general=True).count(),
            '2023 Town Election': voters.filter(v23town=True).count(),
        }
        fig3 = px.bar(x=list(elections.keys()), y=list(elections.values()), title="Voter Participation in Elections")
        context['election_participation_graph'] = fig3.to_html(full_html=False)

        return context