import numpy as np
from dataclasses import dataclass
from scipy.stats import norm
from typing import Union, Tuple
from numpy.typing import NDArray
from numpy import float_
from simulation import geometric_brownian_motion


@dataclass
class BlackScholes():
    sigma: Union[float, NDArray] = None  # volatility in 1-d model or covariance matrix
    r: float = 0

    def __d1d2(
        self,
        T: Union[float, NDArray[float_]],
        K: Union[float, NDArray[float_]],
        S: Union[float, NDArray[float_]]
    ) -> Tuple[Union[float, NDArray[float_]]]:
        """
        Calculates d1 and d2 from Black-Scholes formula.

        Args:
            T: times to maturity.
            K: strikes.
            S: spot prices at t = 0.

        Returns:
            d1: values of d1.
            d2: values of d2.
        """
        d1 = (np.log(S/K) + (self.r + self.sigma**2/2)*T) / (self.sigma*np.sqrt(T))
        d2 = d1 - self.sigma * np.sqrt(T)
        return d1, d2

    def vanilla_price(
        self,
        T: Union[float, NDArray[float_]],
        K: Union[float, NDArray[float_]],
        S: Union[float, NDArray[float_]],
        flag: str
    ) -> Union[float, NDArray[float_]]:
        """
        Calculates the call option price via Black-Scholes formula

        Args:
            T: times to maturity.
            K: strikes.
            S: spot prices at t = 0.
            flag: 'c' for calls, 'p' for puts.

        Returns:
            Prices of the call/put vanilla options.
        """
        d1, d2 = self.__d1d2(T, K, S)
        if flag == 'c':
            return S * norm.cdf(d1) - np.exp(-self.r*T) * K * norm.cdf(d2)
        if flag == 'p':
            return -S * norm.cdf(-d1) + np.exp(-self.r*T) * K * norm.cdf(-d2)

    def vega(
        self,
        T: Union[float, NDArray[float_]],
        K: Union[float, NDArray[float_]],
        S: Union[float, NDArray[float_]],
    ) -> Union[float, NDArray[float_]]:
        """
        Calculates the option vega in the Black-Scholes model

        Args:
            T: times to maturity.
            K: strikes.
            S: spot prices at t = 0.

        Returns:
            Vega of the option(s).
        """
        d1, _ = self.__d1d2(T, K, S)
        return S * norm.pdf(d1) * np.sqrt(T)

    def simulate_trajectory(
        self,
        n_sample: int,
        t_grid: Union[float, NDArray[float_]],
        init_val: Union[float, NDArray[float_]],
        flag: str = "spot",
        random_state: np.random.Generator = None
    ) -> Union[float, NDArray[float_]]:
        """
        Simulates the trajectory of stock or forward in the Black-Scholes model.

        Args:
            n_sample: number of simulated trajectories.
            t_grid: time grid to simulate the price on.
            init_val: the value of process at t = 0.
            flag: "forward" to simulate forward price (without drift). "spot" to simulate spot price.
            random_state: `np.random.Generator` used for simulation

        Returns:
            np.ndarray of shape (n_sample, len(t_grid)) with simulated trajectories if model dimension is 1.
            np.ndarray of shape (n_sample, dim, len(t_grid)) with simulated trajectories if model dimension greater than 1.
        """
        if isinstance(self.sigma, float) or isinstance(self.sigma, int):
            dim = 1
        else:
            dim = len(self.sigma)
        cov = self.sigma**2 if dim == 1 else self.sigma
        drift = self.r if flag == "spot" else 0
        traj = geometric_brownian_motion(
            n_sample=n_sample,
            t_grid=t_grid,
            init_val=init_val,
            drift=drift,
            covariance=cov,
            random_state=random_state
        )
        return traj
