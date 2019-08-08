"""A basic steady-state genetic algorithm."""

from typing import List, Callable
import random

from mhlib.population import Population
from mhlib.scheduler import Method, Scheduler
from mhlib.settings import get_settings_parser
from mhlib.solution import Solution


parser = get_settings_parser()
parser.add("--mh_ssga_cross_prob", type=int, default=1, help='SSGA crossover probability')
parser.add("--mh_ssga_loc_prob", type=int, default=0.1, help='SSGA local improvement probability')


class SteadyStateGeneticAlgorithm(Scheduler):
    """A steady state genetic algorithm.

    During each iteration, one new solution is generated by means
    of crossover and mutation. The new solution
    replaces the worst of the population.

    Attributes
        - sol: solution object, in which final result will be returned
        - meths_ch: list of construction heuristic methods
        - meth_cx: a crossover method
        - meth_mu: a mutation method
        - meth_ls: a local search method
    """

    def __init__(self, sol: Solution, meths_ch: List[Method],
                 meth_cx: Callable[[Solution, Solution], Solution],
                 meth_mu: Method,
                 meth_li: Method,
                 own_settings: dict = None):
        """Initialization.

        :param sol: solution to be improved
        :param meths_ch: list of construction heuristic methods
        :param meth_cx: a crossover method
        :param meth_mu: a mutation method
        :param meth_li: an optional local improvement method
        :param own_settings: optional dictionary with specific settings
        """
        population = Population(sol, meths_ch, own_settings)
        super().__init__(sol, meths_ch + [meth_mu] + [meth_li], own_settings, population=population)
        self.meth_cx = meth_cx
        self.meth_mu = meth_mu
        self.meth_ls = meth_li

        self.incumbent = self.population[self.population.best()]

    def run(self):
        """Actually performs the construction heuristics followed by the SteadyStateGeneticAlgorithm."""

        population = self.population

        while True:
            # Create a new solution
            p1 = population[population.selection()].copy()

            # Optionally crossover
            if random.random() < self.own_settings.mh_ssga_cross_prob:
                p2 = population[population.selection()].copy()
                p1 = self.meth_cx(p1, p2)

            # Mutation
            res = self.perform_method(self.meth_mu, p1)

            if res.terminate:
                break

            # Optionally locally improve
            if self.meth_ls and random.random() < self.own_settings.mh_ssga_loc_prob:
                res = self.perform_method(self.meth_ls, p1)

                if res.terminate:
                    break

            # Replace in population
            worst = population.worst()
            population[worst].copy_from(p1)

            # Update best solution
            if p1.is_better(self.incumbent):
                self.incumbent = p1
