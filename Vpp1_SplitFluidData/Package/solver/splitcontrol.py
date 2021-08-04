from ..parser.inputdatabase import InputDatabase

class SplitControl:

    def __init__(self, path: str):
        
        input_db = InputDatabase.from_file(path)
        self.__input_db = input_db

        # print(input_db)

        # The path of OpenFOAM case
        assert isinstance(input_db["Path"]["case"], str)
        self.__case_path = input_db["Path"]["case"]
        

        # The path of the output file
        assert isinstance(input_db["Path"]["write"], str)
        self.__write_path = input_db["Path"]["write"]

        # Number of the zones in OpenFOAM case
        assert isinstance(input_db["num_zones"], int)
        self.__num_zones = input_db["num_zones"]

        # Determine whether boundary data need to be output
        assert isinstance(input_db["boundary"]["internal"]["write"], bool)
        self.__write_in = input_db["boundary"]["internal"]["write"]

        assert isinstance(input_db["boundary"]["external"]["write"], bool)
        self.__write_out = input_db["boundary"]["external"]["write"]

        # Format of data storage (csv or h5)
        assert isinstance(input_db["write_format"], str)
        self.__write_format = input_db["write_format"]


    def get_case_path(self):

        return self.__case_path

    def get_write_path(self):

        return self.__write_path

    def get_num_zones(self):
        return self.__num_zones

    def whether_write_internal_boundary(self):
        return self.__write_in

    def get_internal_boundary(self):

        if(self.__write_in):
            assert isinstance(self.__input_db["boundary"]["internal"]["index"], list)
            index = self.__input_db["boundary"]["internal"]["index"]

            assert isinstance(self.__input_db["boundary"]["internal"]["name"], list)
            name = self.__input_db["boundary"]["internal"]["name"]
        else:
            quit("No internal boundary data in the control file")

        return index, name

    def whether_write_external_boundary(self):
        return self.__write_out

    def get_external_boundary(self):

        if(self.__write_out):
            assert isinstance(self.__input_db["boundary"]["external"]["index"], list)
            index = self.__input_db["boundary"]["external"]["index"]

            assert isinstance(self.__input_db["boundary"]["external"]["name"], list)
            name = self.__input_db["boundary"]["external"]["name"]
        else:
            quit("No external boundary data in the control file")

        return index, name

    def get_write_format(self):

        return self.__write_format


