import numpy as np
from scipy.stats import norm
from typing import Union
from numpy.typing import NDArray
from numpy import float_
import matplotlib
import matplotlib.pyplot as plt


class MonteCarlo():
    sample: NDArray[float_]
    accuracy: Union[float, NDArray[float_]]
    confidence_level: Union[float, NDArray[float_]]
    mean: Union[float, NDArray[float_]]
    var: Union[float, NDArray[float_]]
    size: int

    def __init__(
        self,
        sample: NDArray[float_],
        confidence_level: Union[float, NDArray[float_]] = None,
        accuracy: Union[float, NDArray[float_]] = None,
        axis: int = 0
    ) -> None:
        """
        Calculates the Monte Carlo statistics for the given sample and the corresponding confidence intervals.

        Args:
            sample: array to compute the mean.
            confidence_level: confidence level for the intervals.
            accuracy: an error estimated via the CLT.
            axis: axis along which the mean to be computed
        """
        self.sample = sample
        self.mean = np.mean(sample, axis=axis)
        self.var = np.var(sample, ddof=1, axis=axis)
        self.size = sample.shape[axis]
        if confidence_level is not None and accuracy is not None:
            raise ValueError('Either accuracy or confidence level should be specified, not both.')
        if confidence_level is not None:
            self.confidence_level = confidence_level
            quantile = norm.ppf((1 + self.confidence_level) / 2)
            self.accuracy = quantile * np.sqrt(self.var / self.size)
        elif accuracy is not None:
            self.accuracy = accuracy
            quantile = accuracy * np.sqrt(self.size / self.var)
            self.confidence_level = 2 * norm.cdf(quantile) - 1
        else:
            raise ValueError('Either accuracy or confidence level should be specified.')

    def convergence_diagram(
        self,
        step: int = 1,
        ax: matplotlib.axes = None,
        plot_intervals: bool = False,
        log: bool = False,
        color: str = 'b',
        label: str = 'MC estimator'
    ):
        """
        Plots a convergence diagram for the given sample.

        Args:
            step: a step used to iterate over the sample.
            ax: axis to plot the diagram.
            plot_intervals: whether to plot confidence intervals.
            log: whether to use log-axis for x.
        """
        if ax is None:
            _, ax = plt.subplots()

        subsample = np.cumsum(self.sample)[step::step]
        ns = np.arange(1, len(subsample) + 1) * step
        means = subsample / ns

        x = np.log(ns) if log else ns
        xlabel = 'log(n)' if log else 'n'

        ax.plot(x, means, color, label=label)
        ax.grid('on')

        if plot_intervals:
            ax.plot(x, means - self.accuracy * np.sqrt(self.size / ns), color + '--', label=f'CI of level {self.confidence_level}')
            ax.plot(x, means + self.accuracy * np.sqrt(self.size / ns), color + '--')
            ax.fill_between(x, means - self.accuracy * np.sqrt(self.size / ns), means + self.accuracy * np.sqrt(self.size / ns), color=color, alpha=0.1)
        ax.legend()
        ax.set_xlabel(xlabel)

    def results(
        self,
        decimals=5
    ) -> str:
        """
        Represents results as a string.

        Args:
            decimals: Number of decimal places to round to.

        Returns:
            String containing mean and accuracy.
        """
        return str(np.round(self.mean, decimals=decimals)) + " ± " + str(np.round(self.accuracy, decimals=decimals))