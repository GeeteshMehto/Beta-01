import re

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from tensorflow.keras.models import load_model
import numpy as np
from sklearn.preprocessing import StandardScaler
import google.generativeai as genai
import joblib
import os
import random
from version_beta import settings

def index(request):


    # Set an environment variable
    # Get the value of an environment variable
    value = os.getenv("api_key")
    print(value)  # Output: some_value

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
        raise ValueError(
            f"City '{str(city).lower()}' is not available. Choose from: {', '.join(location_irradiance.keys())}")

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



# Example function to predict heating and cooling loads
def predict_loads(X1, X2, X3, X4, X5, X6, X7, X8):
    best_model = load_model('model/best_model.keras')
    scaler = joblib.load('model/scaler.pkl')
    X_new = np.array([[X1, X2, X3, X4, X5, X6, X7, X8]])
    X_new_scaled = scaler.transform(X_new)
    y1_pred, y2_pred = best_model.predict(X_new_scaled)
    heating_load = y1_pred[0][0]
    cooling_load = y2_pred[0][0]
    return heating_load, cooling_load


# View for handling form submission
# def predict_view(request):
#     heating_load = None
#     cooling_load = None
#     if request.method == 'POST':
#         # Get form data
#         X1 = float(request.POST.get("X1"))
#         X2 = float(request.POST.get("X2"))
#         X3 = float(request.POST.get("X3"))
#         X4 = float(request.POST.get("X4"))
#         X5 = float(request.POST.get("X5"))
#         X6 = float(request.POST.get("X6"))
#         X7 = float(request.POST.get("X7"))
#         X8 = float(request.POST.get("X8"))
#
#         # Call the prediction function
#         heating_load, cooling_load = predict_loads(X1, X2, X3, X4, X5, X6, X7, X8)
#
#         heating_load = float(heating_load)
#         cooling_load = float(cooling_load)
#
#         # Return the result as a JSON response (to trigger modal with prediction)
#         return JsonResponse({'heating_load': heating_load, 'cooling_load': cooling_load})
#
#     return render(request, 'room.html', {'heating_load': heating_load, 'cooling_load': cooling_load})


def predict_view(request):
    heating_load = None
    cooling_load = None
    fan_hours = None
    ac_hours = None

    if request.method == 'POST':
        # Get form data
        X1 = float(request.POST.get("X1"))
        X2 = float(request.POST.get("X2"))
        X3 = float(request.POST.get("X3"))
        X4 = float(request.POST.get("X4"))
        X5 = float(request.POST.get("X5"))
        X6 = float(request.POST.get("X6"))
        X7 = float(request.POST.get("X7"))
        X8 = float(request.POST.get("X8"))

        # Call the prediction function
        heating_load, cooling_load = predict_loads(X1, X2, X3, X4, X5, X6, X7, X8)

        heating_load = float(heating_load)
        cooling_load = float(cooling_load)

        # Example logic to determine device usage times based on load
        fan_hours = cooling_load / 100  # Sample calculation for fan time
        ac_hours = cooling_load / 500   # Sample calculation for AC time

        # Return the result as a JSON response (to trigger modal with prediction)
        return JsonResponse({
            'heating_load': round(heating_load, 2),
            'cooling_load': round(cooling_load, 2),
            'fan_hours': round(fan_hours*24, 2),
            'ac_hours': round(ac_hours*24, 2)
        })

    return render(request, 'room.html', {'heating_load': heating_load, 'cooling_load': cooling_load})



genai.configure(api_key=settings.api_key)



@csrf_exempt
def gen(request):
    user_message = ""
    bot_response = ""

    if request.method == "POST":
        user_message = request.POST.get("user_message", "")

        if user_message:
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(f"I know you are not expert just tell me genric answer in just 2 to 3 lines and "
                                                  f"be specific about the answer do not go here and there just say answer nothing else "
                                                  f"dont be in doubt just say one answer i know that answer maybe be "
                                                  f"incorrect but just say answer do not say impossible or hard to say just give me one answer "
                                                  f"the question is by User: {user_message}")
                bot_response = response.text if response else "I'm sorry, I couldn't understand that."

            except Exception as e:
                print("Error generating response:", e)
                bot_response = "There was an error generating a response. Please try again."

    return render(request, "gen.html", {"user_message": user_message, "response": bot_response})


def dashboard(request):
    # Generate real-time energy consumption data
    energy_data = {
        'hostels': random.randint(100, 500),
        'academic_buildings': random.randint(500, 1500),
        'research_labs': random.randint(1000, 3000),
        'common_areas': random.randint(200, 1000),
    }

    # Simulate renewable energy sources (solar, wind)
    renewable_data = {
        'solar': random.randint(100, 400),  # Solar energy (in kWh)
        'wind': random.randint(50, 200),  # Wind energy (in kWh)
    }

    # Calculate the total energy consumption
    total_consumption = sum(energy_data.values())

    # Logic to suggest energy diversion
    suggestions = []
    sorted_areas = sorted(energy_data.items(), key=lambda x: x[1])

    low_area, low_value = sorted_areas[0]
    high_area, high_value = sorted_areas[-1]

    if low_value < high_value:
        suggested_transfer = high_value - low_value
        suggestions.append(
            f"Consider diverting {suggested_transfer} kWh from {low_area} to {high_area} to balance the load.")

    # Convert the energy data to JSON to send to the frontend
    energy_data_json = json.dumps(energy_data)
    renewable_data_json = json.dumps(renewable_data)

    return render(request, 'dahsboard.html', {
        'energy_data_json': energy_data_json,
        'renewable_data_json': renewable_data_json,
        'total_consumption': total_consumption,
        'suggestions': suggestions,
    })