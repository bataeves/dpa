__author__ = 'bataev'
from american_option_model import AmericanOptionModel


class AmericanVanillaPutOptionModel(AmericanOptionModel):
  def payoff(self, S):
    return max(self.K - S, 0)
