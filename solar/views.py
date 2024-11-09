from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json


def index(request):
    return render(request, 'index.html')


# Define appliance data with power ratings (in Watts) and typical usage hours per day
equipment_data = {
    "Refrigerator": {"power": 150, "usage_hours": 24},
    "Air Conditioner": {"power": 2000, "usage_hours": 8},
    "Washing Machine": {"power": 500, "usage_hours": 1},
    "Lighting": {"power": 10, "usage_hours": 5},
    "TV": {"power": 120, "usage_hours": 4},
    "Microwave": {"power": 800, "usage_hours": 0.5},
    "Fan": {"power": 75, "usage_hours": 12},
    "Computer": {"power": 300, "usage_hours": 6},
}

# Define solar irradiance data by city (in kWh/m²/day)
location_irradiance = {
    "mumbai": 4.5,
    "delhi": 5.2,
    "chennai": 4.8,
    "bangalore": 5.0,
    "kolkata": 4.6,
    "pune": 5.1,
    "bhopal": 4.9,
    "indore": 5.0
}


def calculate_solar_capacity(appliances, city):
    """
    Calculates the required solar panel capacity for a list of appliances in a given city.

    Parameters:
        appliances (list of dicts): List where each dict has 'name' (appliance), 'quantity', 'power', 'usage_hours'.
        city (str): City name to use the appropriate solar irradiance value.

    Returns:
        float: Required solar panel capacity in kW.
    """
    # Validate city
    if str(city).lower() not in location_irradiance:
        raise ValueError(f"City '{str(city).lower()}' is not available. Choose from: {', '.join(location_irradiance.keys())}")

    # Get the solar irradiance for the specified city
    irradiance = location_irradiance[str(city).lower()]

    # Calculate total daily energy requirement in kWh
    total_energy_kwh = 0
    for appliance in appliances:
        name = appliance["appliance"]
        quantity = appliance["quantity"]

        # Retrieve power and usage hours from default data if not provided
        power = appliance.get("power", equipment_data.get(name, {}).get("power"))
        usage_hours = appliance.get("usageHours", equipment_data.get(name, {}).get("usageHours"))

        if power is None or usage_hours is None:
            raise ValueError(f"Details for appliance '{name}' are missing or not found.")

        # Calculate energy for this appliance and add to total
        daily_energy = (power * usage_hours * quantity) / 1000  # Convert W-hours to kWh
        total_energy_kwh += daily_energy

    # Calculate required solar capacity (kW) based on irradiance
    required_solar_kw = total_energy_kwh / irradiance
    return round(required_solar_kw, 2)


def solarbill(request):
    return render(request, 'solarbill.html')


# # Appliance power data (in watts)
# appliance_power_data = {
#     "Refrigerator": 150,
#     "Air Conditioner": 2000,
#     "Washing Machine": 500,
#     "Lighting": 10,
#     "TV": 120,
#     "Microwave": 800,
#     "Fan": 75,
#     "Computer": 300,
# }

@csrf_exempt
def calculate_solar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        city = str(data.get('city'))
        appliances = data.get('appliances', [])
        # print(appliances)

        solar_requirement_kw = calculate_solar_capacity(city=city, appliances=appliances)
        # solar_requirement_kw = 55

        return JsonResponse({
            'city': city,
            'solar_requirement': solar_requirement_kw
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
