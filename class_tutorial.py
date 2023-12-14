# In Python, a class is a blueprint for creating objects, providing a set of attributes (variables) and methods (functions) that define the behavior and characteristics of those objects.
# It serves as a template to create instances (individual objects) that share the same structure and behavior defined within the class.
class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.is_running = False

    def start(self):
        self.is_running = True
        print(f"The {self.year} {self.make} {self.model} has started.")

    def stop(self):
        self.is_running = False
        print(f"The {self.year} {self.make} {self.model} has stopped.")

# Creating instances of the Car class
car1 = Car("Toyota", "Camry", 2020)
car2 = Car("Tesla", "Model S", 2022)

# Accessing attributes and calling methods of the objects
print(car1.make)  # Output: Toyota
print(car2.year)  # Output: 2022


car1.start()  # Output: The 2020 Toyota Camry has started.
car2.stop()   # Output: The 2022 Tesla Model S has stopped.
