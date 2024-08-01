import numpy as np
from experiment_logging.base_logging_connector import BaseLoggingConnector

import wandb


class WandBConnector(BaseLoggingConnector):
    """Logging connector for Weights and Biases."""

    # TODO: Add type hints for the class variables, polish the implementation
    def __init__(self):
        self.run = None

    def start(self, config: dict | None = None):
        self.run = wandb.init(project="alphagomoku", save_code=True, config=config)

    def log(self, log_dict: dict):
        assert self.run is not None, "WandBConnector is not started, call start()"
        wandb.log(log_dict)

    def log_array(self, array_name: str, array: np.ndarray):
        """Given a 2D array, log it as a heatmap."""
        assert self.run is not None, "WandBConnector is not started, call start()"
        assert array.ndim == 2, "Array must be 2D"
        wandb.log({array_name: wandb.Image(array)})

    def finish(self):
        assert self.run is not None, "WandBConnector is not started, call start()"
        self.run.finish()
