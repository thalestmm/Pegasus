from django.shortcuts import render
from .forms import CarpForm
from .scripts.carp_calculator import CarpCalculator, PDF


# Create your views here.


def carp_form(request):
    if request.method == "POST":

        data = request.POST
        form = CarpForm(data)

        if form.is_valid():
            data_package = form.cleaned_data

            carp_data = CarpCalculator(values=data_package).full_execute()

            name, trigram, today, carp_vectors, launch_axis, unit, chute_amount, chute_selection, \
            parachute_limits, pressure, temperature, drop_height, speed = carp_data

            pdf = PDF(name, trigram, carp_vectors, launch_axis, unit, chute_amount, chute_selection,
                      parachute_limits, pressure, temperature, drop_height, speed)

            # return render_mission(request, form_data=form.cleaned_data, package=request.POST.items())
            return None

    else:
        form = CarpForm()

    return render(request, "carp/carp_form.html", {
        "form": form
    })
