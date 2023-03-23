class Display:
    def __init__(self, text: str=''):
        self.text = text

    def updateText(self, text: str):
        if self.text != text:
            self.text = text
            self.__drawText(text)

    def turnOn(self):
        pass

    def turnOff(self):
        pass

    def __drawText(self, text: str):
        pass