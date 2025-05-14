class Car:
    def __init__(self, brand, wheels, color, speed, weightParameter):
        self.brand = brand
        self.wheels = wheels
        self.color = color
        self.speed = speed
        self.weight = weightParameter
        self.accessory = None

    def honk(self):
        print("HONK HONK")

    def printDetails(self):
        print("THE DETAILS ARE")
        print(self.brand)
        print(self.wheels)
        print(self.color)
        print(self.speed)
        print(self.weight)
        print(self.accessory)
    
    def addAccessory(self, accessory1):
        self.accessory = accessory1
    

myCar = Car("Mitsubishi", 4, "Red", "50 km/h", "600 kg")

myCar.honk()
myCar.printDetails()
print(myCar.brand)
print(myCar.wheels)
print(myCar.color)
print(myCar.speed)
print(myCar.weight)
