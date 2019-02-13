
class GraphData: 

    def __init__(self, planner): 
        self._planner = planner

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value): 
        self.set(key, value)

    def get(self, *args):
        data = self._planner.get_data()

        # if no arguments were given
        if not args: 
            return data

        if len(args) == 1:
            return data[args[0]]

        result = {}

        for arg in args: 
            result[arg] = data.get(arg)
        
        return result
        
    def set(self, *args, **kargs):
        if len(args) == 1 and type(args[0]) is dict: 
            for key, value in args[0].items():
                self._planner.set_data(key, value)

            return 
        
        if (len(args) == 2): 
            self._planner.set_data(args[0], args[1])

            return 

        for key, value in kargs.items(): 
            self._planner.set_data(key, value)
