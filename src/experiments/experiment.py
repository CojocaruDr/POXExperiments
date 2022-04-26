class Experiment:

    def __init__(self):
        pass

    def run(self):
        """
        Runs the given experiment. Some experiments might need to call #configure first.
        :return:
        """
        raise RuntimeError("Experiment must implement run method.")

    def configure(self, **kwargs):
        """
        Stores experiment parameters, run any pre-experiment setup needed.
        :param kwargs: experiment data and config information
        :return:
        """
        pass