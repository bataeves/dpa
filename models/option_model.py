from base_model import BaseModel


class OptionModel(BaseModel):
  """docstring for OptionModel"""

  def __init__(self, **kwargs):
    super(OptionModel, self).__init__()
    self.K = kwargs.get("K")
    self.T = kwargs.get("T")
    self.asset = kwargs.get("asset")
