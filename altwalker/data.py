
class GraphData:
    """Read and update the current data values for the current model.

    Uses Planner's ``get_data`` and ``set_data`` to read and update the
    current data for the model.
    """

    def __init__(self, planner):
        self._planner = planner

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def get(self, *args):
        """Get the current data values for the current model.

        Args:
            *args: The keys, if no args are provided the method wiil return
                all data available.

        Returns:
            A dictionary containing all data for no ``*args`` or containing
            all the keys in ``*args`` for more than one.

            If only one ``*args`` is provided will return only the value of that key.
        """

        data = self._planner.get_data()

        if not args:
            return data

        if len(args) == 1:
            return data[args[0]]

        result = {}

        for arg in args:
            result[arg] = data.get(arg)

        return result

    def set(self, *args, **kargs):
        """Set data in the current model.

        Args:
            *args: A ``dict`` or a two ``*args`` a key followed by the new value.
            **kargs: Each key will be set equal to it's value.
        """

        if len(args) == 1 and type(args[0]) is dict:
            for key, value in args[0].items():
                self._planner.set_data(key, value)

            return

        if (len(args) == 2):
            self._planner.set_data(args[0], args[1])

            return

        for key, value in kargs.items():
            self._planner.set_data(key, value)
