## Overview
Trophotracker is an inverse optimization where you input desired values (protein, fat, carbs, calories) and a list of foods, using which the tool uses constrained optimisation algorithms and USDA API data to determine ideal food portions to hit your nutritional targets.


### Pre-requisites
1. Install requests scipy
   
   pip install requests scipy

3. Get free USDA FoodData API key:
   
   Visit [USDA FoodData Central API](https://fdc.nal.usda.gov/api-guide.html)
   
   Click "Get an API Key" and sign up with your email
   
   Replace "apikey" with key you received via email in code
   

## Technical
Formula: Loss = Σ ((actual - target) / target)²

Algorithm: SLSQP (Sequential Least Squares Programming)


## Limitations
The USDA API has rate limits, so avoid making hundreds of queries rapidly

Food names must be specific (e.g., "chicken breast" not "chicken")

Each food is limited to 0-800g portions

Some target combinations may be mathematically impossible with chosen foods
