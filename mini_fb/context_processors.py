# mini_fb/context_processors.py
from .models import Profile

def add_profile(request):
    if request.user.is_authenticated:
        try:
            return {'profile': request.user.profile}
        except Profile.DoesNotExist:
            # Handle cases where the user has no profile
            return {'profile': None}
    return {}