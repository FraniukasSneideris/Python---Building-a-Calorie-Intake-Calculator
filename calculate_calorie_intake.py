import json  
from collections import defaultdict
from difflib import get_close_matches


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


def main():
    interactive_instance = Interactive("nutrition.json")  
    interactive_instance.interactive_mode()

if __name__ == "__main__":
    main()
