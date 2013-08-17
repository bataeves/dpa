#include<gsl/gsl_sf_erf.h>


#! Call premium
def Call(S, K, r, Vol, theta):
  #!S : Stock price --- K : Strike --- r: riskless interest rate 
  #!Vol: volatility --- theta: time to maturity
  if (S > 0):
    standard_deviation = Vol * sqrt(theta)
    d1 = (log(S / K) + r * theta) / standard_deviation + 0.5 * standard_deviation
    d2 = d1 - standard_deviation
    return S * gsl_sf_erf_Q(-d1) - K * exp(-r * theta) * gsl_sf_erf_Q(-d2);
  else:
    return 0


#! Put premium
def Put(double S, double
K, double
r, double
Vol, double
theta):
#!S : Stock price --- K : Strike --- r: riskless interest rate
#!Vol: volatility --- theta: time to maturity
if (S > 0):
  standard_deviation = Vol * sqrt(theta)
  d1 = (log(S / K) + r * theta) / standard_deviation + 0.5 * standard_deviation
  d2 = d1 - standard_deviation
  return -S * gsl_sf_erf_Q(d1) + K * exp(-r * theta) * gsl_sf_erf_Q(d2)
else:
  return K * exp(-r * theta)
