from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from .forms import MissionPlannerForm, AirportInputField
from .models import Project

from .functions.flight_planner import FlightPlan
from .functions.decea_api import DeceaApiConnection
from .functions.gramet_scraping import GrametScraper

from django.shortcuts import Http404

from django.views.decorators.csrf import csrf_protect

# Create your views here.


@csrf_protect
def planner_form(request):
    available_projects = Project.objects.all()

    airport_form       = AirportInputField()
    rows_to_render     = range(1)

    if request.method == "POST":
        # TODO: ADD VALIDATION BEFORE SUBMITTING TO CHECK IF ALL THE ICAO ARE ON
        # TODO: THE DB

        # TODO: FIND A BETTER WAY TO SOLVE THIS REFERENCING ISSUE
        aircraft_registry = str(request.POST['project']).split(' ')[1]

        form = MissionPlannerForm(
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
        form = MissionPlannerForm()

    return render(request, "mission_planner/planner_form.html",
                  {"form": form,
                   "projects": available_projects,
                   "rows": rows_to_render,
                   "airport_form": airport_form})


def render_mission(request, form_data, package):
    header = form_data

    extra_data = ['csrfmiddlewaretoken', 'project', 'trip_weight', 'takeoff_time']

    package_dict = {c[0]: c[1] for c in package}

    for key in extra_data:
        package_dict.pop(key)

    try:
        fp = FlightPlan(
            project=header['project'],
            trip_weight=header['trip_weight'],
            takeoff_time=header['takeoff_time'],
            flight_plan_legs=package_dict
        )

        # DATA PAYLOADS FROM API
        data_package    = {} # A DICT OF DICTS
        meteoro_package = {}
        hours_package   = {}

        gramet_scraper = GrametScraper(icao_route=fp.icao_route)
        gramet_url     = gramet_scraper.gramet_url

        empty_list      = []

        for airport in fp.all_fpl_airports:
            api = DeceaApiConnection()
            api.get_notam_from_icao(airport)

            if len(api.data_output) == 0:
                data_package[airport] = [False]
            else:
                data_package[airport] = api.data_output

            api = DeceaApiConnection()
            api.get_meteoro_data_from_icao(airport)

            meteoro_package[airport] = api.data_output

        return render(request, "mission_planner/render_mission.html",
                      {"project": header['project'],
                       "rows": enumerate(fp.export_data),
                       "total_hours": fp.total_hours,
                       "working_hours": fp.working_hours,
                       "data_package": zip(data_package.keys(), data_package.items()),
                       "empty_list": empty_list,
                       "meteoro_package": zip(meteoro_package.keys(), meteoro_package.items()),
                       'gramet_url': gramet_url if gramet_url is not None else False})

    except IndexError:
        # TODO: HANDLE MISSING ICAO TO EXPLAIN WHY THE STATUS WAS RAISED
        print(e)
        raise Http404()

