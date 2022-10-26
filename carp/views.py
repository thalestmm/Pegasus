from django.shortcuts import render
from .forms import CarpForm


# Create your views here.


def carp_form(request):
    if request.method == "POST":

        form = CarpForm(
            {
                "project": Project.objects.get(registry=aircraft_registry),
                "trip_weight": request.POST['trip_weight'],
                "takeoff_time": request.POST['takeoff_time']
            }
        )

        if form.is_valid():
            # TODO: ADD FLIGHT PLANNING LOGIC AND SEND REQUEST TO NEXT VIEW

            return render_mission(request, form_data=form.cleaned_data, package=request.POST.items())

    else:
        form = CarpForm()

    return render(request, "carp/carp_form.html", {
        "form": form
    })
