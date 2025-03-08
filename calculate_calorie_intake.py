import json  
from collections import defaultdict
from difflib import get_close_matches


class FoodDatabase:
    """
    A class to manage food nutrition data from a JSON file.
    
    This class provides methods to read, write, and search for food nutrition data, 
    as well as a dictionary for common food weight conversions.
    
    Attributes:
        unit_conversions (dict): A dictionary mapping common food terms to their approximate weight in grams.
    """
    unit_conversions = {"egg": 50, "banana": 118, "apple": 200, "orange": 130, "kiwi": 70,
                        "slice of bread": 30, "loaf of bread": 500, "cup of rice": 200, "cup of oats": 80, 
                        "cup of flour": 120, "tablespoon of butter": 14, "tablespoon of peanut butter": 16, 
                        "tablespoon of sugar": 12, "teaspoon of salt": 6, "potato": 150, "sweet potato": 130, 
                        "chicken breast": 180, "steak": 250, "fillet of salmon": 200}

    def __init__(self, file):
        """
        Initializes the FoodDatabase by loading nutrition data from a file.
        
        Args:
            file (str): The path to the JSON file containing nutrition data.
        """
        self.nutrition_dict = self.read_file(file)
        
    def read_file(self, file):
        """
        Reads the nutrition data from a JSON file.
        
        Args:
            file (str): The path to the JSON file.
            
        Returns:
                dict: A dictionary containing nutrition data.
        """
        with open(file, 'r') as json_file:
            nutrition_dict = json.load(json_file)
            return nutrition_dict
        
    def write_file(self, file, data):
        """
        Writes updated food data to the JSON file.
        
        Args:
            file (str): The path to the JSON file.
            data (dict): The new food data to be written to the file.
            
        Modifies:
                The JSON file at the given path.
        """
        with open(file, "w") as f: 
            json.dump(data, f, indent=4)
            
    def find_closest_match(self, food, food_list):
        """
        Finds the closest match for a food item using fuzzy matching.
        
        Args:
            food (str): The food item to search for.
            food_list (list): A list of available food items.
            
        Returns:
                str or None: The closest matching food item, or None if no match is found.
        """
        food_list = list(self.nutrition_dict.keys()) + list(self.unit_conversions.keys())
        matches = get_close_matches(food, food_list, n=1, cutoff=0.6)
        return matches[0] if matches else None


class Nutrition():
    """
    A class for calculating and displaying the nutritional summary of meals.
    
    This class allows users to:
      - Compute the total nutritional values for a meal.
      - Display a formatted nutritional summary.
      - Add new food items to the nutrition database.
      
    Attributes:
        fdb (FoodDatabase): An instance of FoodDatabase for managing nutrition data.
    """
    def __init__(self, file):
        """
        Initializes the Nutrition by loading nutrition data from a file.
        
        Args:
            file (str): The path to the JSON file containing nutrition data.

        Attributes:
            fdb: An instance of FoodDatabase.
        """
        self.fdb = FoodDatabase(file)

    def nutritional_summary(self, ndict):
        """
        Computes the total nutritional content of a meal.
        
        Args:
            ndict (dict): A dictionary where keys are food items (str) and values are quantities (float).
        
        Returns:
            dict: A dictionary containing the total nutritional values for the meal.
        """
        output_dict = defaultdict(float)  
        food_list = list(self.fdb.nutrition_dict.keys()) + list(self.fdb.unit_conversions.keys())  
        
        for key, value in ndict.items():
            matched_key = self.fdb.find_closest_match(key, food_list)
            
            if matched_key in self.fdb.unit_conversions:
                grams = self.fdb.unit_conversions[matched_key] * value if value < 10 else value
                matched_key = self.fdb.find_closest_match(matched_key, list(self.fdb.nutrition_dict.keys()))
                value = grams  

            if matched_key in self.fdb.nutrition_dict:
                for k, v in self.fdb.nutrition_dict[matched_key].items():
                    output_dict[k] += (float(v) * value) / 100

        return dict(output_dict)
    
    def print_clean_output(self, final_dict):
        """
        Prints the nutritional summary in a user-friendly format.

        Args:
            final_dict (dict): A dictionary containing nutritional values.

        Prints:
            A formatted nutritional summary.
        """
        for key, value in final_dict.items():
            
            if key == "calories":
                print(f"{key.title()}:".ljust(17) + f"{int(value):>6} kcal")
            else:
                print(f"{key.replace('_', ' ').title()}:".ljust(17) + f"{int(value):>6} g")
    
    def add_new_food(self, food, cal, fat, prot, carb, sug):
        """
        Adds a new food item to the nutrition database.

        Args:
            food (str): The name of the new food item.
            cal (float): The kilocalories in the food item.
            fat (float): The amount of fat (g).
            prot (float): The amount of protein (g).
            carb (float): The amount of carbohydrates (g).
            sug (float): The amount of sugars (g).

        Returns:
            dict: A dictionary containing the nutritional details of the new food item.

        Modifies:
            The "nutrition.json" file by adding the new food item.
        """
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
            existing_data = self.fdb.read_file("nutrition.json")
        except (FileNotFoundError, json.JSONDecodeError):  
            existing_data = {}  
            
        existing_data.update(new_item)
        self.fdb.write_file("nutrition.json", existing_data)  
        self.fdb.nutrition_dict.update(new_item)
        print("✅ New food added successfully!")
        
        return new_item


class Interactive:
    """
    A class for interactive calorie intake tracking.
    
    This class allows users to input food items and their quantities, 
    check if they exist in the food database, add new food items if needed, 
    and view a running nutritional summary.
    
    Attributes:
        fdb (FoodDatabase): Instance of FoodDatabase for retrieving nutritional information.
        nutr (Nutrition): Instance of Nutrition for processing and displaying nutritional data.
    """
    
    def __init__(self, file):
        """
        Initializes the Interactive class with a food database and nutrition processor.

        Args:
            file (str): The path to the nutrition database file.
        """
        self.fdb = FoodDatabase(file)
        self.nutr = Nutrition(file)
    
    def handle_invalid_input(self, emoji, act1, act2):
        """
        Handles invalid user input by prompting for valid responses.

        Args:
            emoji (str): An emoji to display in the prompt.
            act1 (str): The primary action described in the prompt.
            act2 (str): The secondary action for additional clarity.

        Returns:
            str: 'y' if the user confirms, 'n' otherwise.
        """
        while True:
            a = input(f"\n{emoji} Would you like to {act1} food (y/n): ").strip().lower()
            if a in ("y", "n"):
                return a
            print(f"❌ Invalid input. Please enter 'y' to {act2}, otherwise enter 'n'.")
    
    def interactive_mode(self):
        """
        Runs the interactive mode for food entry and nutritional tracking.

        Users can input food items, specify quantities, and receive a real-time 
        nutritional summary. If a food item is not found in the database, they are 
        given an option to add it manually.
        
        Prints:
            A running total of the user's nutritional intake.
        """
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
                print("❌ Invalid quantity. Please enter a number.\n")
                continue

            if food not in self.fdb.nutrition_dict:
                print(f"⚠️ {food} was not found in database.\n")
                
                addition = self.handle_invalid_input("💾", "save", "save new food")
                    
                if addition == "y":
                    while True:
                        try:
                            cal = float(input(f"Enter kcal for {food} every 100 g: "))
                            fat = float(input(f"Enter g of total fat for {food} every 100 g: "))
                            prot = float(input(f"Enter g of protein for {food} every 100 g: "))
                            carb = float(input(f"Enter g of carbohydrates for {food} every 100 g: "))
                            sug = float(input(f"Enter g of sugar for {food} every 100 g: "))
                            break
                        except ValueError:
                            print("⚠️ Please enter valid numbers (whole or decimal values only).\n")

                    self.nutr.add_new_food(food, cal, fat, prot, carb, sug)

            summary = self.nutr.nutritional_summary(meals)
            print("\n🟢 Current Total:")
            self.nutr.print_clean_output(summary)

            continuation = self.handle_invalid_input("➕", "add more", "continue")

            if continuation == "n":
                break
    
        print("\n✅ Final Nutritional Summary:")
        self.nutr.print_clean_output(summary)


def main():
    """
    The main function that starts the interactive calorie intake tracking.

    This function initializes the Interactive class with a given nutrition database file
    and starts the interactive mode, allowing users to input food items, track their nutritional
    intake, and add new food items if needed.

    Usage:
        Run this function to start the interactive calorie intake calculator.

    Modifies:
        The "nutrition.json" file if the user adds new food items.
    """
    interactive_instance = Interactive("nutrition.json")  
    interactive_instance.interactive_mode()

if __name__ == "__main__":
    main()
