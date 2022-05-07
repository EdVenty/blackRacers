import json
import os

class Storage:
    def __init__(self, filename: str, encoding: str = 'utf-8') -> None:
        self.filename = filename
        self.encoding = encoding

    def save(self):
        """Stores annotated values from object into config file.
        """
        if os.path.exists(self.filename):
            os.remove(self.filename)
        with open(self.filename, 'w', encoding=self.encoding) as file:
            file.write(json.dumps([{
                "name": a,
                "type": str(self.__annotations__[a])[8:-2],
                "value": getattr(self, a)
            } for a in self.__annotations__]))

    def load(self):
        """Loads values from configuration into storage object.

        Raises:
            FileNotFoundError: File does not exists.
        """
        if os.path.exists(self.filename):
            raise FileNotFoundError(f"File {self.filename} does not exists.")
        with open(self.filename, 'r', encoding=self.encoding) as file:
            for var in json.loads(file.read()):
                typeobj = getattr(__builtins__, var['type'])
                setattr(self, var['name'], typeobj(var['value']))
