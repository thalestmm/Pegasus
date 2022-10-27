from django.shortcuts import render, HttpResponse
from django.http import FileResponse
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

            return FileResponse(open(pdf.filename, 'rb'), as_attachment=True, filename=pdf.filename)

    else:
        form = CarpForm()

    return render(request, "carp/carp_form.html", {
        "form": form
    })
