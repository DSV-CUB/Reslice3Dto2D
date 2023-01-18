import pickle
import os

from tools.__basics__ import functions


class Inheritance:
    def __init__(self, **kwargs):
        self.path_rw = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "data")
        self.name = "CMR Tools"
        self.version = "0.1"
        self.date = "2022-02-17"
        self.author = "Darian Steven Viezzer"
        self.contact = "Charité Campus Buch\nExperimental and Clinical Research Center\na joint institution of Charité and MDC\nAG CMR\nLindenberger Weg 80\n13125 Berlin\nGermany\nE-Mail: darian-steven.viezzer@charite.de"
        return

    def set(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and not functions.check_class_has_method(self, key) and not key == "path":
                exec("self." + key + " = kwargs.get(\"" + key + "\", None)")
        return True

    def save(self, path=None, timestamp=""):
        if path is None:
            save_to = self.path_rw
        else:
            save_to = path

        if save_to.endswith(".pickle"):
            with open(save_to, 'wb') as file:
                pickle.dump(self, file)
                file.close()
        else:

            if not timestamp == "":
                save_to = os.path.join(save_to, timestamp)

            os.makedirs(save_to, exist_ok=True)

            self.set(path_rw=save_to)

            with open(os.path.join(save_to, self.name.lower() + ".pickle"), 'wb') as file:
                pickle.dump(self, file)
                file.close()
        return True

    def load(self, path=None):
        if path is None or not path.endswith(".pickle"):
            load_from = os.path.join(self.path_rw, self.name.lower() + ".pickle")
        else:
            load_from = path

        try:
            with open(load_from, 'rb') as file:
                obj = pickle.load(file)
                file.close()

            if type(self) == type(obj):
                for key in obj.__dict__:
                    if key in self.__dict__ and key not in ["version", "author", "contact", "date"]:
                        self.__dict__[key] = obj.__dict__[key]
                self.path_rw = load_from
            else:
                raise TypeError("The loaded object is not a configuration object")
        except:
            pass

        return True

    def reset(self):
        self.__init__()
        return

