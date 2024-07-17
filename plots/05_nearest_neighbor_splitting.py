import pandas as pd
import numpy as np
from typing import Tuple
from scipy.spatial.distance import cdist
import paint.util.paint_mappings as mappings

class NearestNeighborSplit:
    """
    @brief Splits a dataset by the euclidean solar position distance of its data points. 
    Selects the data points of largest nearest neighbor distance for validation 
    and constructs the training data from the remaining data points.
    """

    def __init__(self,
                 number_of_train_samples: int,
                 number_of_validation_samples: int):
        """
        @brief constructor

        @param number_of_train_samples : int
            The number of samples used for training.
        @param number_of_validation_samples : int
            The number of samples used for validation.

        """
        self._number_of_train_samples = number_of_train_samples
        self._number_of_validation_samples = number_of_validation_samples
    
    def _metric(self, lhs : np.ndarray, rhs : np.ndarray) -> np.ndarray:
        """
        @brief Internal method used for computing the distance between two given data points.

        @param lhs : np.ndarray the left hand side operator [azimuth, elevation, index]
        @param rhs : np.ndarray the right hand side operator [azimuth, elevation, index]

        @return Euclidean distance between lhs and rhs azimuth and elevation if their index is not equal else np.inf
        """
        return np.inf if lhs[2] == rhs[2] else np.linalg.norm(lhs[:2] - rhs[:2])

    def sort(self, data : pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        @brief Sorts the given data points by their nearest neighbor distance and constructs a training and validation data split.

        @param data Input data to be split into training and validation.

        @return one data frame each for training and validation data in this order
        """
        if (len(data) < self._number_of_train_samples + self._number_of_validation_samples):
            raise RuntimeError(f"Insufficient data points given. Expected at least {self._number_of_train_samples + self._number_of_validation_samples} but got {len(data)}!")
        
        # sort data by nearest neighbor distance
        # TODO maybe use kd-tree for distance calculation
        distances = cdist(data[[mappings.AZIMUTH, mappings.ELEVATION, mappings.ID_INDEX]], data[[mappings.AZIMUTH, mappings.ELEVATION, mappings.ID_INDEX]], metric=self._metric)
        minimum_distances = np.sort(distances, axis=1)[:,0]
        sorted_indices = np.argsort(minimum_distances, axis=0)

        # use data with largest nearest neighbor distance for validation
        validation_data = data.iloc[sorted_indices[-self._number_of_validation_samples:]]

        # use remaining data for training
        training_data = data.iloc[sorted_indices[-(self._number_of_train_samples + self._number_of_validation_samples):-self._number_of_validation_samples]]

        return training_data, validation_data        
    
if __name__ == "__main__":

    data = {
        mappings.AZIMUTH: [1, 2, 5, 8, 9, 12],
        mappings.ELEVATION: [3, 4, 6, 10, 10, 15],
        mappings.ID_INDEX: [0,1,2,3,4,5]
    }

    split = NearestNeighborSplit(number_of_train_samples=2, number_of_validation_samples=3)
    training_data, validation_data = split.sort(data=pd.DataFrame(data))