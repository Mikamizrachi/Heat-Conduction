class Body:
    def __init__(self, mass, specific_heat, temp):
        if mass <= 0:
            print("Mass must be greater then 0")

        if specific_heat <= 0:
            print("Specific heat must be greatr than 0")

        if temp < 0:
            print("Temperature must be 0 or above")

        self.mass = mass
        self.specific_heat = specific_heat
        self.temp = temp


    def add_heat(self, heat):
        delta_t = heat / (self.mass * self.specific_heat)

        self.temp = self.temp + delta_t
        return self.temp

    test



    







