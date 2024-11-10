from django.shortcuts import render
from django.views.generic import ListView
from .models import Voter
from .forms import VoterFilterForm
from django.db.models import Q
from django.views.generic import DetailView

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'  # Custom template name
    context_object_name = 'voters'
    paginate_by = 100  # Display 100 voters per page

    def get_queryset(self):
        queryset = Voter.objects.all()
        form = VoterFilterForm(self.request.GET)

        if form.is_valid():
            # Filter by party affiliation (ensure correct field mapping)
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
                    q_objects &= Q(**{election: True})  # This assumes the election field name matches the form key
                queryset = queryset.filter(q_objects)  # Apply the filter

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VoterFilterForm(self.request.GET)  # Preserve form data
        return context

class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'