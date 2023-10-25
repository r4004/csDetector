class customException(list):
    def __init__(self, input_list, list_name):
        super().__init__(input_list)
        self.list_name = list_name

    def printError(self):
        if not self:
            raise ValueError(f"ERROR, the list {self.list_name} is void")