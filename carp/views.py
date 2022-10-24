from django.shortcuts import render

# Create your views here.


def carp_form(request):
    return render(request, 'carp/carp_form.html', {})