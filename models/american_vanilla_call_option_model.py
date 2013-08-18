__author__ = 'bataev'
from american_option_model import AmericanOptionModel


class AmericanVanillaCallOptionModel(AmericanOptionModel):
  def payoff(self, S):
    return max(S - self.K, 0)
