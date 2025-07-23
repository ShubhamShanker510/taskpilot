# A context processor injects data into all templates globally (or selectively, with conditions).


# users/context_processors.py
def user_data(request):
    if request.user.is_authenticated and request.path.startswith("/dashboard"):
        return {"user": request.user}
    return {}
