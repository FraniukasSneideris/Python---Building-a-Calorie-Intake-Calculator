# Python---Building-a-Calorie-Intake-Calculator
![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Project Overview
This project is an expanded version of a simple calorie intake calculator. It started as a small challenge from a DataCamp project, where the task was to build a single function. However, I wanted to create something more functional, and thus, this fully-fledged calorie intake calculator was born. With this tool, users can easily input food items and quantities, receive nutritional summaries, and even add new food items to the database.

---

## Key Features
- **Nutritional Summary:** The program calculates the total calories, fat, protein, carbohydrates, and sugar content of your meals based on the food and quantities you input.
- **Food Database:** A pre-existing database containing common foods and their nutritional values, including unit conversions for items like eggs, fruits, and more.
- **Interactive Mode:** Users can input food items and quantities via a Command Line Interface (CLI). If a food is not found, they can add it directly to the database.
- **Dynamic Data Management:** Allows users to expand the food database by adding new foods with their nutritional values.

---

## Libraries Used
- **`json`**: Used to handle file operations (reading and writing data in JSON format).
- **`collections.defaultdict`**: Helps to initialize dictionary values with a default type (in this case, float) to easily accumulate food quantities.
- **`difflib.get_close_matches`**: Used to find the closest match for a food item when there’s a typo or variation in input.

---

## Context

What started as a one function script, turned into a more complex Object-Oriented Programming structured script. 

However, everything has a beginning so let's start there:

The DataCamp project requests the student to define a function which takes data from a json file, and calculates calorie intake for the entered food and amount. The argument of said function (as requested by DataCamp) should be a dictionary specifying food as the key, and quantity as the value. 

The code I first wrote was this:
```python
import json
from collections import defaultdict

with open('nutrition.json', 'r') as json_file:
    nutrition_dict = json.load(json_file)

def nutritional_summary(ndict):
    output_dict = defaultdict(float)  
    
    for key, value in ndict.items():
        
        if key in nutrition_dict:
            for k, v in nutrition_dict[key].items():
                output_dict[k] += (v * value) / 100
                
        else:
            return key  
    
    return dict(output_dict)

# Provided example to try the function
nutritional_summary({"Croissants, cheese": 150, "Orange juice, raw": 250})
```
Quite a simple function, which creates an empty defaultidct (hence collections) and then loops in the dictionary provided by the user (ndict), checking if the keys are in the json dictionary (nutrition_dict), and then basically returning a new dictionary which takes the calories, total_fat, protein, carbs and sugar from the json data, and multiplies it by the amount entered by the user, returning the meal nutritional information.

So for example, after calling the function as showed before, we get an output like this:
```bash
{'calories': 733.5,
 'total_fat': 32.0,
 'protein': 15.55,
 'carbohydrate': 96.5,
 'sugars': 38.025}
```
Now, this is fine and all, but it is too basic. There's not much we can do with that code.

So this is why I decided to write something better..

## Final Code
I wrote a nice script with OOP structure, which uses collections.defaultdict and difflib.get_close_matches, allows for user input, and also allows the user to store new data into the json file if the script does not find a match for the food entered.

The code is structured using three main classes: `FoodDatabase`, `Nutrition`, and `Interactive`. Here's an explanation of each class:

### 1. **FoodDatabase**
The `FoodDatabase` class manages the food database, reading from and writing to the JSON file. It includes:
- **`unit_conversions`**: A dictionary of common units like eggs, bananas, and cups, with their corresponding weights in grams.
- **`read_file()`**: Reads and loads the food data from a JSON file.
- **`write_file()`**: Writes updated food data back to the JSON file.
- **`find_closest_match()`**: Uses `get_close_matches()` to find the closest match for a food item, helping with input errors or slight variations in names.
```python
class FoodDatabase:
    unit_conversions = {"egg": 50, "banana": 118, "apple": 200, "orange": 130, "kiwi": 70,
                        "slice of bread": 30, "loaf of bread": 500, "cup of rice": 200, "cup of oats": 80, 
                        "cup of flour": 120, "tablespoon of butter": 14, "tablespoon of peanut butter": 16, 
                        "tablespoon of sugar": 12, "teaspoon of salt": 6, "potato": 150, "sweet potato": 130, 
                        "chicken breast": 180, "steak": 250, "fillet of salmon": 200}

    def __init__(self, file):
        self.file = file
        self.nutrition_dict = self.read_file(file)
        
    def read_file(self, file):
        with open(file, 'r') as json_file:
            nutrition_dict = json.load(json_file)
            return nutrition_dict
        
    def write_file(self, file, data):
        with open(file, "w") as f: 
            json.dump(data, f, indent=4)
            
    def find_closest_match(self, food, food_list):
        food_list = list(self.nutrition_dict.keys()) + list(self.unit_conversions.keys())
        matches = get_close_matches(food, food_list, n=1, cutoff=0.6)
        return matches[0] if matches else None
```

### 2. **Nutrition**
The `Nutrition` class inherits from `FoodDatabase` and calculates the nutritional summary of a meal based on the food items and their quantities.
- **`nutritional_summary()`**: Takes a dictionary of food items and quantities, and computes the total nutritional content.
- **`print_clean_output()`**: Displays the nutritional summary in a user-friendly format.
- **`add_new_food()`**: Allows users to add a new food item to the database with its nutritional details.
```python
class Nutrition(FoodDatabase):
    def __init__(self, file):
        super().__init__(file)
        
    def nutritional_summary(self, ndict):
        output_dict = defaultdict(float)  
        food_list = list(self.nutrition_dict.keys()) + list(self.unit_conversions.keys())  
        
        for key, value in ndict.items():
            matched_key = self.find_closest_match(key, food_list)
            
            if matched_key in self.unit_conversions:
                grams = self.unit_conversions[matched_key] * value if value < 10 else value
                matched_key = self.find_closest_match(matched_key, list(self.nutrition_dict.keys()))
                value = grams  

            if matched_key in self.nutrition_dict:
                for k, v in self.nutrition_dict[matched_key].items():
                    output_dict[k] += (float(v) * value) / 100

        return dict(output_dict)
    
    def print_clean_output(self, final_dict):
        for key, value in final_dict.items():
            
            if key == "calories":
                print(f"{key.title()}:".ljust(17) + f"{int(value):>6} kcal")
            else:
                print(f"{key.replace('_', ' ').title()}:".ljust(17) + f"{int(value):>6} g")
    
    def add_new_food(self, food, cal, fat, prot, carb, sug):
        new_item = {
            food: {
                "calories": cal,
                "total_fat": fat,
                "protein": prot,
                "carbohydrate": carb,
                "sugars": sug 
            }
        }
        
        try:
            existing_data = self.read_file("nutrition.json")
        except (FileNotFoundError, json.JSONDecodeError):  
            existing_data = {}  
            
        existing_data.update(new_item)
        self.write_file("nutrition.json", existing_data)  
        self.nutrition_dict.update(new_item)
        print("✅ New food added successfully!")
        
        return new_item
```

### 3. **Interactive**
The `Interactive` class extends the `Nutrition` class and handles user interaction via the CLI. In other words, this is where the magic happens!
- **`interactive_mode()`**: This method manages the main logic of the program, allowing users to input food items, quantities, and interact with the food database. If a food item is not found, users are prompted to add it to the database.
```python
class Interactive(Nutrition):
    def __init__(self, file):
        super().__init__(file)
    
    def interactive_mode(self):
        meals = defaultdict(float)

        print("Welcome to Calorie Intake Calculator! 😊 \n")
        print("How to use? 🤔\n")
        print("Just enter food   🥑🍕🍔🍣🥩🥕🍩🍇🌮🧀")
        print("and quantity (grams/units) ⚖️ 🔢📐📊📏🥄\n")
        print("That's it! 😎 \n")

        while True:
            food = input("Enter food item: ").strip()
            quantity = input(f"Enter quantity for {food}: ").strip()

            try:
                quantity = float(quantity)
                meals[food] += quantity
            except ValueError:
                print("❌ Invalid quantity. Please enter a number.")
                continue

            if food not in self.nutrition_dict:
                print(f"⚠️ {food} was not found in database.\n")
                addition = input("Would you like to add this food into the database? (y/n): ").strip().lower()
                if addition == "y":
                    cal = input(f"Enter kcal for {food} every 100 g: ")
                    fat = input(f"Enter g of total fat for {food} every 100 g: ")
                    prot = input(f"Enter g of protein for {food} every 100 g: ")
                    carb = input(f"Enter g of carbohydrates for {food} every 100 g: ")
                    sug = input(f"Enter g of sugar for {food} every 100 g: ")
                    self.add_new_food(food, cal, fat, prot, carb, sug)

            summary = self.nutritional_summary(meals)
            print("\n🟢 Current Total:")
            self.print_clean_output(summary)

            continuation = input("\n➕ Would you like to add more food? (y/n): ").strip().lower()
            if continuation != "y":
                break
    
        print("\n✅ Final Nutritional Summary:")
        self.print_clean_output(summary)
```
---

## How to Use
1. Clone the repository or download the script to your local machine.
2. Make sure you have Python installed (Python 3.6 or higher recommended).
3. Run the script on your preferred IDE:
   ```bash
   python calorie_calculator.py
   ```
4. Interactive Mode:
   You’ll be prompted to enter a food item and its quantity.
   If the food is not found in the database, you’ll be given an option to add it, along with its nutritional values (calories, fat, protein, carbs, and sugar).
   The calculator will provide a summary of the total calories, fat, protein, carbohydrates, and sugar for the foods entered.

Example output:
```bash
Welcome to Calorie Intake Calculator! 😊 

How to use? 🤔

Just enter food   🥑🍕🍔🍣🥩🥕🍩🍇🌮🧀
and quantity (grams/units) ⚖️ 🔢📐📊📏🥄

That's it! 😎 

Enter food item: chicken
Enter quantity for chicken: 200

🟢 Current Total:
Calories:           220 kcal
Total Fat:           30 g
Protein:             40 g
Carbohydrate:         0 g
Sugars:               0 g

➕ Would you like to add more food? (y/n): y
Enter food item:
```
5. Adding new food:

Now, let's say you enter a food that it's not found in the json database.. If that happens, you'll get the following:
```bash
Enter food item: cupcake
Enter quantity for cupcake: 1
⚠️ cupcake was not found in database.

Would you like to add this food into the database? (y/n):
```
If you select "y", then you'll be able to enter the nutritional data for that food macronutrient by macronutrient, like so:
```bash
Enter kcal for cupcake every 100 g: 
Enter g of total fat for cupcake every 100 g: 
Enter g of protein for cupcake every 100 g: 
Enter g of carbohydrates for cupcake every 100 g: 
Enter g of sugar for cupcake every 100 g:
```
Once all the data is entered, you'll get a message that says that the new food was added. This new addition will remain the dictionary, so next time you use the program, you won't need to add the food again!

You'll get a Current Total, and again the program will ask if you want to add more food. When you select "n", you'll get a Final Total, and the program will stop running.
```bash
✅ Final Nutritional Summary:
Calories:           220 kcal
Total Fat:           30 g
Protein:             40 g
Carbohydrate:         0 g
Sugars:               0 g
```

---

## Conclusion
This project is a comprehensive Python-based calorie intake calculator designed to help users track their nutritional intake in a simple, interactive way. It offers a combination of flexible features, from handling a pre-existing food database to allowing users to add new foods, making it highly extensible. Here are the key features:

- **Nutritional Summary**: The script calculates the total calories, fats, proteins, carbohydrates, and sugars of the foods entered, based on their quantities.
- **Food Database**: It includes a pre-defined database with common food items and their nutritional values, with unit conversions available for different measurements (e.g., grams, cups, and individual pieces of food like eggs or bananas).
- **Error Handling and Flexibility**: If the user enters a food item that isn't in the database, they’re offered the option to add it. This makes the tool more dynamic and constantly evolving.
- **Interactive Command-Line Interface (CLI)**: A user-friendly CLI guides users through the process, making it easy for anyone to use regardless of technical expertise.
- **Extensible Database**: The ability to expand the database by adding new foods directly through the interface means that it can grow as needed to suit different users' diets and preferences.
- **Detailed and Clear Output**: Nutritional information is printed in a clean, easy-to-read format, with clear distinctions between different categories of nutrients.

With these features combined, this tool offers both practicality and flexibility for anyone looking to monitor their dietary intake, whether they are tracking their daily nutrition or just trying to understand the nutritional content of their meals better.

This project demonstrates how Python can be used for practical applications in data management, user interaction, and expanding datasets dynamically. It offers an excellent foundation for anyone interested in developing similar projects or building more complex applications in data processing and nutrition tracking.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.





