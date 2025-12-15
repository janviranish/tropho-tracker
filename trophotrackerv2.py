import requests
from scipy.optimize import minimize
API_KEY = "apikey"

#Get nutrition data per 100g of food from API
def nutrition(name):
    try:
        r = requests.get( 'https://api.nal.usda.gov/fdc/v1/foods/search',
            params={"query": name, "api_key": API_KEY, "pageSize": 1, "dataType": ["Foundation", "SR Legacy"]})
        data = r.json()
        if not data.get('foods'):
            return None

        food = data['foods'][0]
        nutrients = {n['nutrientName']: n['value'] for n in food['foodNutrients']}

        return {'name': food['description'],'protein': nutrients.get('Protein', 0),
            'fat': nutrients.get('Total lipid (fat)', 0), 'carbs': nutrients.get('Carbohydrate, by difference', 0),
            'calories': nutrients.get('Energy', 0)}
    except:
        return None

#Calculate total nutrition from combinations of amount
def total_nutrition(amounts, food_data):
    totals = {'protein': 0, 'fat': 0, 'carbs': 0, 'calories': 0}
    for amount, food in zip(amounts, food_data):
        for key in totals:
            totals[key] += (amount / 100.0) * food[key]
    return totals

#Find portion for nutrition target
def portion_size(targets, food_names, preferred=None, fixed=None):
    food_data = [nutrition(name) for name in food_names]
    if any(f is None for f in food_data):
        raise ValueError("Could not find all foods")

    n = len(food_data)
    preferred = preferred or [100.0] * n

    bounds = [(preferred[i], preferred[i]) if (fixed and fixed[i]) else (0.0, 800.0) for i in range(n)]
    #Assess choice with squared errors
    def objective(amounts):
        current = total_nutrition(amounts, food_data)
        loss = sum(((current.get(k, 0) - targets.get(k, 0)) / targets.get(k, 1)) ** 2
                   for k in ["protein", "fat", "carbs", "calories"])
        num_used = sum(1 for a in amounts if a > 20)
        loss += max(0, 3 - num_used) * 2.0
        return loss

    result = minimize(objective, preferred, bounds=bounds, method="SLSQP")
    if not result.success:
        print(f"Warning: {result.message}")

    return result.x, food_data

#Main block to run code and get inputs
if __name__ == "__main__":
    print("Welcome to the TrophoTracker!")
    print("Let's get started.")
    print("Enter your nutrition targets:")
    targets = {
        'protein': float(input("Protein (g): ")),
        'fat': float(input("Fat (g): ")),
        'carbs': float(input("Carbs (g): ")),
        'calories': float(input("Calories (kcal): "))
    }
    print("\nList food or enter to stop:")
    foods = []
    while True:
        food = input("Food: ").strip()
        if not food:
            break
        foods.append(food)

    # Exit run
    if not foods:
        exit()

    amounts, food_data = portion_size(targets, foods)
    final = total_nutrition(amounts, food_data)

    print("\nNutrition Plan:")
    for food, amt in zip(foods, amounts):
        print(f"  {food}: {amt:.0f}g")

    print(f"\nResults:")
    for key in ["protein", "fat", "carbs", "calories"]:
        error = abs(final[key] - targets[key]) / targets[key] * 100
        unit = "kcal" if key == "calories" else "g"
        print(f"  {key.capitalize()}: {final[key]:.1f}{unit} (target: {targets[key]}{unit}, {error:.1f}% error)")