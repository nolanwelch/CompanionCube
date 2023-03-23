class Switch:
    def __init__(self, pin: int):
        self.pin = pin

    def isPressed(self) -> bool:
        pass

class LightSensor:
    def __init__(self, pin: int):
        self.pin = pin

    def getLevel(self):
        return

class LED:
    def __init__(self, pin: int):
        self.pin = pin
        self.isOn = False

    def turnOn(self):
        pass

    def turnOff(self):
        pass

    def toggle(self):
        if self.isOn:
            self.turnOff()
        else:
            self.turnOn()