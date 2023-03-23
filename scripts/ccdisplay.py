class Display:
    def __init__(self, text: str=''):
        self.text = text

    def updateText(self, text: str):
        self.text = text
        self.__drawText(text)

    def __drawText(self, text: str):
        pass