from ..parser.inputdatabase import InputDatabase

class TheoryControl:

    def __init__(self, path: str):
        
        input_db = InputDatabase.from_file(path)

        # print(input_db)

        # geometric model
        assert isinstance(input_db["model"]["geometry"], str)
        self.__geometry = input_db["model"]["geometry"]

        # the motion of the boundary
        assert isinstance(input_db["model"]["motion"], str)
        self.__motion = input_db["model"]["motion"]

        # the virtual flow
        assert isinstance(input_db["model"]["virtualmotion"], str)
        self.__virtualflow = input_db["model"]["virtualmotion"]
        

    def get_geometry(self):

        return self.__geometry

    def get_motion(self):

        return self.__motion

    def get_virtualmotion(self):
        return self.__virtualflow


