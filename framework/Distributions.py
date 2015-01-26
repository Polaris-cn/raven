'''
Created on Mar 7, 2013

@author: crisr
'''
#for future compatibility with Python 3--------------------------------------------------------------
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)
#End compatibility block for Python 3----------------------------------------------------------------

#External Modules------------------------------------------------------------------------------------
import sys
import copy
import numpy as np
import scipy.special as polys
from scipy.misc import factorial
#External Modules End--------------------------------------------------------------------------------

#Internal Modules------------------------------------------------------------------------------------
from BaseClasses import BaseType
from utils import returnPrintTag, returnPrintPostTag, find_distribution1D
distribution1D = find_distribution1D()
#Internal Modules End--------------------------------------------------------------------------------

stochasticEnv = distribution1D.DistributionContainer.Instance()

'''
 Mapping between internal framework and Crow distribution name
'''
_FrameworkToCrowDistNames = {'Uniform':'UniformDistribution',
                              'Normal':'NormalDistribution',
                              'Gamma':'GammaDistribution',
                              'Beta':'BetaDistribution',
                              'Triangular':'TriangularDistribution',
                              'Poisson':'PoissonDistribution',
                              'Binomial':'BinomialDistribution',
                              'Bernoulli':'BernoulliDistribution',
                              'Logistic':'LogisticDistribution',
                              'Exponential':'ExponentialDistribution',
                              'LogNormal':'LogNormalDistribution',
                              'Weibull':'WeibullDistribution'  }


class Distribution(BaseType):
  '''
  a general class containing the distributions
  '''
  def __init__(self):
    BaseType.__init__(self)
    self.upperBoundUsed = False  # True if the distribution is right truncated
    self.lowerBoundUsed = False  # True if the distribution is left truncated
    self.upperBound       = 0.0  # Right bound
    self.lowerBound       = 0.0  # Left bound
    self.__adjustmentType   = '' # this describe how the re-normalization to preserve the probability should be done for truncated distributions
    self.dimensionality   = None # Dimensionality of the distribution (1D or ND)
    self.printTag         = returnPrintTag('DISTRIBUTIONS')

  def _readMoreXML(self,xmlNode):
    '''
    Readmore xml, see BaseType.py explaination.
    '''
    if xmlNode.find('upperBound') !=None:
      self.upperBound = float(xmlNode.find('upperBound').text)
      self.upperBoundUsed = True
    if xmlNode.find('lowerBound')!=None:
      self.lowerBound = float(xmlNode.find('lowerBound').text)
      self.lowerBoundUsed = True
    if xmlNode.find('adjustment') !=None: self.__adjustment = xmlNode.find('adjustment').text
    else: self.__adjustment = 'scaling'

  def getCrowDistDict(self):
    '''
    Returns a dictionary of the keys and values that would be
    used to create the distribution for a Crow input file.
    '''
    retDict = {}
    retDict['type'] = _FrameworkToCrowDistNames[self.type]
    if self.lowerBoundUsed:
      retDict['xMin'] = self.lowerBound
    if self.upperBoundUsed:
      retDict['xMax'] = self.upperBound
    return retDict

  def addInitParams(self,tempDict):
    '''
    Function to get the input params that belong to this class
    @ In, tempDict, temporary dictionary
    '''
    tempDict['upperBoundUsed'] = self.upperBoundUsed
    tempDict['lowerBoundUsed'] = self.lowerBoundUsed
    tempDict['upperBound'    ] = self.upperBound
    tempDict['lowerBound'    ] = self.lowerBound
    tempDict['adjustmentType'] = self.__adjustmentType
    tempDict['dimensionality'] = self.dimensionality

  def rvsWithinCDFbounds(self,LowerBound,upperBound):
    '''
    Function to get a random number from a truncated distribution
    @ In, LowerBound, float -> lower bound
    @ In, upperBound, float -> upper bound
    @ In,           , float -> random number
    '''
    point = float(np.random.rand(1))*(upperBound-LowerBound)+LowerBound
    return self._distribution.InverseCdf(point)

  def rvsWithinbounds(self,LowerBound,upperBound):
    '''
    Function to get a random number from a truncated distribution
    @ In, LowerBound, float -> lower bound
    @ In, upperBound, float -> upper bound
    @ Out,          , float -> random number
    '''
    CDFupper = self._distribution.Cdf(upperBound)
    CDFlower = self._distribution.Cdf(LowerBound)
    return self.rvsWithinCDFbounds(CDFlower,CDFupper)

  def setQuad(self,quad,exp_order):
    '''
    Function to set the quadrature rule
    @ In, quad, object -> quadrature
    @ In, exp_order, int -> expansion order
    @ Out,         , None
    '''
    self.__distQuad=quad
    self.__exp_order=exp_order

  def quad(self):
    try: return self.__distQuad
    except AttributeError: raise IOError (self.printTag+': ' +returnPrintPostTag('ERROR') + '-> No quadrature has been set for this distr. yet.')

  def polyOrder(self):
    try: return self.__exp_order
    except AttributeError: raise IOError (self.printTag+': ' +returnPrintPostTag('ERROR') + '-> Quadrature has not been set for this distr. yet.')

def random():
  '''
  Function to get a random number <1<
  @ In, None, None
  @ Out, float, random number
  '''
  return stochasticEnv.random()

def randomSeed(value):
  '''
  Function to get a random seed
  @ In, None, None
  @ Out, integer, random seed
  '''
  return stochasticEnv.seedRandom(value)

def randomIntegers(low,high):
  '''
  Function to get a random integer
  @ In, low, integer -> low boundary
  @ In, high, integer -> upper boundary
  @ Out, integer, random int
  '''
  int_range = high-low
  raw_num = low + random()*int_range
  raw_int = int(round(raw_num))
  if raw_int < low or raw_int > high:
    print("Random int out of range")
    raw_int = max(low,min(raw_int,high))
  return raw_int

def randomPermutation(l):
  '''
  Function to get a random permutation
  @ In, l, list -> list to be permuted
  @ Out, list, randomly permuted list
  '''
  new_list = []
  old_list = l[:]
  while len(old_list) > 0:
    new_list.append(old_list.pop(randomIntegers(0,len(old_list)-1)))
  return new_list

class BoostDistribution(Distribution):
  '''
  Base distribution class based on boost
  '''
  def __init__(self):
    Distribution.__init__(self)
    self.dimensionality  = '1D'
    self.disttype        = 'Continuous'

  def cdf(self,x):
    '''
    Function to get the cdf at a provided coordinate
    @ In, x, float -> value to get the cdf at
    @ Out, flaot, requested cdf
    '''
    return self._distribution.Cdf(x)

  def ppf(self,x):
    '''
    Function to get the inverse cdf at a provided coordinate
    @ In, x, float -> value to get the inverse cdf at
    @ Out, flaot, requested inverse cdf
    '''
    return self._distribution.InverseCdf(x)

  def pdf(self,x):
    '''
    Function to get the pdf at a provided coordinate
    @ In, x, float -> value to get the pdf at
    @ Out, flaot, requested pdf
    '''
    return self._distribution.Pdf(x)

  def untruncatedCdfComplement(self, x):
    '''
    Function to get the untruncated  cdf complement at a provided coordinate
    @ In, x, float -> value to get the untruncated  cdf complement  at
    @ Out, flaot, requested untruncated  cdf complement
    '''
    return self._distribution.untrCdfComplement(x)

  def untruncatedHazard(self, x):
    '''
    Function to get the untruncated  Hazard  at a provided coordinate
    @ In, x, float -> value to get the untruncated  Hazard   at
    @ Out, flaot, requested untruncated  Hazard
    '''
    return self._distribution.untrHazard(x)

  def untruncatedMean(self):
    '''
    Function to get the untruncated  Mean
    @ In, None
    @ Out, flaot, requested Mean
    '''
    return self._distribution.untrMean()

  def untruncatedMedian(self):
    '''
    Function to get the untruncated  Median
    @ In, None
    @ Out, flaot, requested Median
    '''
    return self._distribution.untrMedian()

  def untruncatedMode(self):
    '''
    Function to get the untruncated  Mode
    @ In, None
    @ Out, flaot, requested Mode
    '''
    return self._distribution.untrMode()

  def rvs(self,*args):
    '''
    Function to get random numbers
    @ In, args, dictionary, args
    @ Out, flaot or list, requested random number or numbers
    '''
    if len(args) == 0: return self.ppf(random())
    else             : return [self.rvs() for _ in range(args[0])]
#==============================================================\
#    Distributions convenient for stochastic collocation
#==============================================================\

class Uniform(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.low = 0.0
    self.hi = 0.0
    self.type = 'Uniform'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['xMin'] = self.low
    retDict['xMax'] = self.hi
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self,xmlNode)
    low_find = xmlNode.find('low')
    if low_find != None: self.low = float(low_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> low value needed for uniform distribution')
    hi_find = xmlNode.find('hi')
    high_find = xmlNode.find('high')
    if hi_find != None: self.hi = float(hi_find.text)
    elif high_find != None: self.hi = float(high_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> hi or high value needed for uniform distribution')
#    self.initializeDistribution() this call is done by the sampler each time a new step start
    self.range=self.hi-self.low
    # check if lower or upper bounds are set, otherwise default
    if not self.upperBoundUsed:
      self.upperBoundUsed = True
      self.upperBound     = self.hi
    if not self.lowerBoundUsed:
      self.lowerBoundUsed = True
      self.lowerBound     = self.low
    #assign associated polynomial types
    self.polynomial = polys.legendre
    #define functions locally, then point to them
    def norm(n):
      '''Returns normalization constant for polynomial type, given the poly ordeir'''
      return np.sqrt((2.*n+1.)/2.)

    def standardToActualPoint(x): #standard -> actual
      '''Given a [-1,1] point, converts to parameter value.'''
      return x*self.range/2.+self._distribution.mean()

    def actualToStandardPoint(x): #actual -> standard
      '''Given a parameter value, converts to [-1,1] point.'''
      return (x-self._distribution.mean())/(self.range/2.)

    def standardToActualWeight(x): #standard -> actual
      '''Given normal quadrature weight, returns adjusted weight.'''
      return x/(self.range/2.)

    def probNorm(x): #normalizes probability if total != 1
      '''Returns the poly factor to scale by so that sum(probability)=1.'''
      return self.range

    # point to functions
    self.poly_norm = norm
    self.actual_point = standardToActualPoint
    self.std_point = actualToStandardPoint
    self.actual_weight = standardToActualWeight
    self.probability_norm = probNorm

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self,tempDict)
    tempDict['low'] = self.low
    tempDict['hi'] = self.hi
    # no other additional parameters required

  def initializeDistribution(self):
    self._distribution = distribution1D.BasicUniformDistribution(self.low,self.low+self.range)


class Normal(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.mean  = 0.0
    self.sigma = 0.0
    self.type = 'Normal'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['mu'] = self.mean
    retDict['sigma'] = self.sigma
    return retDict


  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    mean_find = xmlNode.find('mean' )
    if mean_find != None: self.mean  = float(mean_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> mean value needed for normal distribution')
    sigma_find = xmlNode.find('sigma')
    if sigma_find != None: self.sigma = float(sigma_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> sigma value needed for normal distribution')
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['mean' ] = self.mean
    tempDict['sigma'] = self.sigma

  def initializeDistribution(self):
    if (not self.upperBoundUsed) and (not self.lowerBoundUsed):
      self._distribution = distribution1D.BasicNormalDistribution(self.mean,
                                                                  self.sigma)
      self.polynomial = polys.hermitenorm
      def norm(n):
        return (np.sqrt(np.sqrt(2.*np.pi)*factorial(n)))**(-1)

      def standardToActualPoint(x): #standard -> actual
        return x*self.sigma**2/2.+self._distribution.mean()

      def actualToStandardPoint(x): #actual -> standard
        return (x-self._distribution.mean())/(self.sigma**2/2.)

      def standardToActualWeight(x): #standard -> actual
        return x/(self.sigma**2/2.)

      def probNorm(_): #normalizes if total prob. != 1
        return 1.0

      self.poly_norm = norm
      self.actual_point = standardToActualPoint
      self.std_point = actualToStandardPoint
      self.actual_weight = standardToActualWeight
      self.probability_norm = probNorm
      self.lowerBound = -sys.float_info.max
      self.upperBound =  sys.float_info.max
    else:
      if self.debug: print('FIXME: this should be removed.... :special case distribution for stochastic colocation')
      if self.lowerBoundUsed == False:
        a = -sys.float_info.max
        self.lowerBound = a
      else:a = self.lowerBound
      if self.upperBoundUsed == False:
        b = sys.float_info.max
        self.upperBound = b
      else:b = self.upperBound
      self._distribution = distribution1D.BasicNormalDistribution(self.mean,
                                                                  self.sigma,
                                                                  a,b)

class Gamma(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.low = 0.0
    self.alpha = 0.0
    self.beta = 1.0
    self.type = 'Gamma'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['k'] = self.alpha
    retDict['theta'] = 1.0/self.beta
    retDict['low'] = self.low
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self,xmlNode)
    low_find = xmlNode.find('low')
    if low_find != None: self.low = float(low_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> low value needed for Gamma distribution')
    alpha_find = xmlNode.find('alpha')
    if alpha_find != None: self.alpha = float(alpha_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> alpha value needed for Gamma distribution')
    beta_find = xmlNode.find('beta')
    if beta_find != None: self.beta = float(beta_find.text)
    else: self.beta=1.0
    # check if lower bound are set, otherwise default
    if not self.lowerBoundUsed:
      self.lowerBoundUsed = True
      self.lowerBound     = self.low
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self,tempDict)
    tempDict['low'] = self.low
    tempDict['alpha'] = self.alpha
    tempDict['beta'] = self.beta

  def initializeDistribution(self):
    if (not self.upperBoundUsed) and (not self.lowerBoundUsed):
      self._distribution = distribution1D.BasicGammaDistribution(self.alpha,1.0/self.beta,self.low)
      self.lowerBoundUsed = 0.0
      self.upperBound     = sys.float_info.max
    else:
      if self.lowerBoundUsed == False:
        a = 0.0
        self.lowerBound = a
      else:a = self.lowerBound
      if self.upperBoundUsed == False:
        b = sys.float_info.max
        self.upperBound = b
      else:b = self.upperBound
      self._distribution = distribution1D.BasicGammaDistribution(self.alpha,1.0/self.beta,self.low,a,b)

    self.polynomial = polys.genlaguerre
    def norm(n):
      return np.sqrt(factorial(n)/polys.gamma(n+self.alpha+1.0))

    def standardToActualPoint(x): #standard -> actual
      return x/self.alpha+self.alpha+self.low #TODO these correct? no beta used

    def actualToStandardPoint(x): #actual -> standard
      return (x-self.low-self.alpha)*self.alpha

    def standardToActualWeight(x): #standard -> actual
      return x

    def probNorm(_): #normalizes probability if total != 1
      return 1.0

    self.poly_norm=norm
    self.actual_point = standardToActualPoint
    self.std_point = actualToStandardPoint
    self.actual_weight = standardToActualWeight
    self.probability_norm = probNorm

class Beta(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.low = 0.0
    self.hi = 1.0
    self.alpha = 0.0
    self.beta = 0.0
    self.type = 'Beta'
    if self.debug: print('FIXME: # TODO default to specific Beta distro?')
    # TODO default to specific Beta distro?

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['alpha'] = self.alpha
    retDict['beta'] = self.beta
    retDict['scale'] = self.hi-self.low
    return retDict


  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self,xmlNode)
    low_find = xmlNode.find('low')
    if low_find != None: self.low = float(low_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> low value needed for Beta distribution')
    hi_find = xmlNode.find('hi')
    high_find = xmlNode.find('high')
    if hi_find != None: self.hi = float(hi_find.text)
    elif high_find != None: self.hi = float(high_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> hi or high value needed for Beta distribution')
    alpha_find = xmlNode.find('alpha')
    if alpha_find != None: self.alpha = float(alpha_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> alpha value needed for Beta distribution')
    beta_find = xmlNode.find('beta')
    if beta_find != None: self.beta = float(beta_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> beta value needed for Beta distribution')
    # check if lower or upper bounds are set, otherwise default
    if not self.upperBoundUsed:
      self.upperBoundUsed = True
      self.upperBound     = self.hi
    if not self.lowerBoundUsed:
      self.lowerBoundUsed = True
      self.lowerBound     = self.low
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self,tempDict)
    tempDict['low'] = self.low
    tempDict['hi'] = self.hi
    tempDict['alpha'] = self.alpha
    tempDict['beta'] = self.beta

  def initializeDistribution(self):
    if (not self.upperBoundUsed) and (not self.lowerBoundUsed):
      self._distribution = distribution1D.BasicBetaDistribution(self.alpha,self.beta,self.hi-self.low)
    else:
      if self.lowerBoundUsed == False: a = 0.0
      else:a = self.lowerBound
      if self.upperBoundUsed == False: b = sys.float_info.max
      else:b = self.upperBound
      self._distribution = distribution1D.BasicBetaDistribution(self.alpha,self.beta,self.hi-self.low,a,b)

#==========================================================\
#    other distributions
#==========================================================\


# Add polynomials, shifting, zero-to-one to these!
class Triangular(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.apex = 0.0
    self.min  = 0.0
    self.max  = 0.0
    self.type = 'Triangular'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['xPeak'] = self.apex
    retDict['lowerBound'] = self.min
    retDict['upperBound'] = self.max
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    apex_find = xmlNode.find('apex')
    if apex_find != None: self.apex = float(apex_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> apex value needed for normal distribution')
    min_find = xmlNode.find('min')
    if min_find != None: self.min = float(min_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> min value needed for normal distribution')
    max_find = xmlNode.find('max')
    if max_find != None: self.max = float(max_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> max value needed for normal distribution')
    # check if lower or upper bounds are set, otherwise default
    if not self.upperBoundUsed:
      self.upperBoundUsed = True
      self.upperBound     = self.max
    if not self.lowerBoundUsed:
      self.lowerBoundUsed = True
      self.lowerBound     = self.min
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['apex' ] = self.apex
    tempDict['min'  ] = self.min
    tempDict['max'  ] = self.max

  def initializeDistribution(self):
    if (self.lowerBoundUsed == False and self.upperBoundUsed == False) or (self.min == self.lowerBound and self.max == self.upperBound):
      self._distribution = distribution1D.BasicTriangularDistribution(self.apex,self.min,self.max)
    else:
      raise IOError (self.printTag+': ' +returnPrintPostTag('ERROR') + '-> Truncated triangular not yet implemented')


class Poisson(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.mu  = 0.0
    self.type = 'Poisson'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['mu'] = self.mu
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    mu_find = xmlNode.find('mu')
    if mu_find != None: self.mu = float(mu_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> mu value needed for poisson distribution')
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['mu'  ] = self.mu

  def initializeDistribution(self):
    if self.lowerBoundUsed == False and self.upperBoundUsed == False:
      self._distribution = distribution1D.BasicPoissonDistribution(self.mu)
      self.lowerBound = 0.0
      self.upperBound = sys.float_info.max
    else:
      raise IOError (self.printTag+': ' +returnPrintPostTag('ERROR') + '-> Truncated poisson not yet implemented')


class Binomial(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.n       = 0.0
    self.p       = 0.0
    self.type     = 'Binomial'
    self.disttype = 'Descrete'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['n'] = self.n
    retDict['p'] = self.p
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    n_find = xmlNode.find('n')
    if n_find != None: self.n = float(n_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> n value needed for Binomial distribution')
    p_find = xmlNode.find('p')
    if p_find != None: self.p = float(p_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> p value needed for Binomial distribution')
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['n'  ] = self.n
    tempDict['p'  ] = self.p

  def initializeDistribution(self):
    if self.lowerBoundUsed == False and self.upperBoundUsed == False:
      self._distribution = distribution1D.BasicBinomialDistribution(self.n,self.p)
    else: raise IOError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> Truncated Binomial not yet implemented')
#
#
#
class Bernoulli(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.p        = 0.0
    self.type     = 'Bernoulli'
    self.disttype = 'Descrete'
    self.lowerBound = 0.0
    self.upperBound = 1.0

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['p'] = self.p
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    p_find = xmlNode.find('p')
    if p_find != None: self.p = float(p_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> p value needed for Bernoulli distribution')
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['p'  ] = self.p

  def initializeDistribution(self):
    if self.lowerBoundUsed == False and self.upperBoundUsed == False:
      self._distribution = distribution1D.BasicBernoulliDistribution(self.p)
    else:  raise IOError (self.printTag+': ' +returnPrintPostTag('ERROR') + '-> Truncated Bernoulli not yet implemented')

  def cdf(self,x):
    if x <= 0.5: return self._distribution.Cdf(self.lowerBound)
    else       : return self._distribution.Cdf(self.upperBound)

  def pdf(self,x):
    if x <= 0.5: return self._distribution.Pdf(self.lowerBound)
    else       : return self._distribution.Pdf(self.upperBound)

  def untruncatedCdfComplement(self, x):
    if x <= 0.5: return self._distribution.untrCdfComplement(self.lowerBound)
    else       : return self._distribution.untrCdfComplement(self.upperBound)

  def untruncatedHazard(self, x):
    if x <= 0.5: return self._distribution.untrHazard(self.lowerBound)
    else       : return self._distribution.untrHazard(self.upperBound)
#
#
#
class Logistic(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.location  = 0.0
    self.scale = 1.0
    self.type = 'Logistic'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['scale'] = self.scale
    retDict['location'] = self.location
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    location_find = xmlNode.find('location')
    if location_find != None: self.location = float(location_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> location value needed for Logistic distribution')
    scale_find = xmlNode.find('scale')
    if scale_find != None: self.scale = float(scale_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> scale value needed for Logistic distribution')
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['location'] = self.location
    tempDict['scale'   ] = self.scale

  def initializeDistribution(self):
    if self.lowerBoundUsed == False and self.upperBoundUsed == False:
      self._distribution = distribution1D.BasicLogisticDistribution(self.location,self.scale)
    else:
      if self.lowerBoundUsed == False: a = -sys.float_info.max
      else:a = self.lowerBound
      if self.upperBoundUsed == False: b = sys.float_info.max
      else:b = self.upperBound
      self._distribution = distribution1D.BasicLogisticDistribution(self.location,self.scale,a,b)


class Exponential(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.lambda_var = 1.0
    self.type = 'Exponential'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['lambda'] = self.lambda_var
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    lambda_find = xmlNode.find('lambda')
    if lambda_find != None: self.lambda_var = float(lambda_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> lambda value needed for Exponential distribution')
    # check if lower bound is set, otherwise default
    if not self.lowerBoundUsed:
      self.lowerBoundUsed = True
      self.lowerBound     = 0.0
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['lambda'] = self.lambda_var

  def initializeDistribution(self):
    if (self.lowerBoundUsed == False and self.upperBoundUsed == False):
      self._distribution = distribution1D.BasicExponentialDistribution(self.lambda_var)
      self.lowerBound = 0.0
      self.upperBound = sys.float_info.max
    else:
      if self.lowerBoundUsed == False:
        a = 0.0
        self.lowerBound = a
      else:a = self.lowerBound
      if self.upperBoundUsed == False:
        b = sys.float_info.max
        self.upperBound = b
      else:b = self.upperBound
      self._distribution = distribution1D.BasicExponentialDistribution(self.lambda_var,a,b)


class LogNormal(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.mean = 1.0
    self.sigma = 1.0
    self.type = 'LogNormal'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['mu'] = self.mean
    retDict['sigma'] = self.sigma
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    mean_find = xmlNode.find('mean')
    if mean_find != None: self.mean = float(mean_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> mean value needed for LogNormal distribution')
    sigma_find = xmlNode.find('sigma')
    if sigma_find != None: self.sigma = float(sigma_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> sigma value needed for LogNormal distribution')
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['mean' ] = self.mean
    tempDict['sigma'] = self.sigma

  def initializeDistribution(self):
    if self.lowerBoundUsed == False and self.upperBoundUsed == False:
      self._distribution = distribution1D.BasicLogNormalDistribution(self.mean,self.sigma)
      self.lowerBound = -sys.float_info.max
      self.upperBound =  sys.float_info.max
    else:
      if self.lowerBoundUsed == False:
        a = -sys.float_info.max
        self.lowerBound = a
      else:a = self.lowerBound
      if self.upperBoundUsed == False:
        b = sys.float_info.max
        self.upperBound = b
      else:b = self.upperBound
      self._distribution = distribution1D.BasicLogNormalDistribution(self.mean,self.sigma,a,b)


class Weibull(BoostDistribution):
  def __init__(self):
    BoostDistribution.__init__(self)
    self.lambda_var = 1.0
    self.k = 1.0
    self.type = 'Weibull'

  def getCrowDistDict(self):
    retDict = Distribution.getCrowDistDict(self)
    retDict['lambda'] = self.lambda_var
    retDict['k'] = self.k
    return retDict

  def _readMoreXML(self,xmlNode):
    BoostDistribution._readMoreXML(self, xmlNode)
    lambda_find = xmlNode.find('lambda')
    if lambda_find != None: self.lambda_var = float(lambda_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> lambda (scale) value needed for Weibull distribution')
    k_find = xmlNode.find('k')
    if k_find != None: self.k = float(k_find.text)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> k (shape) value needed for Weibull distribution')
    # check if lower  bound is set, otherwise default
    if not self.lowerBoundUsed:
      self.lowerBoundUsed = True
      # lower bound = 0 since no location parameter available
      self.lowerBound     = 0.0
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    BoostDistribution.addInitParams(self, tempDict)
    tempDict['lambda'] = self.lambda_var
    tempDict['k'     ] = self.k

  def initializeDistribution(self):
    if (self.lowerBoundUsed == False and self.upperBoundUsed == False) or self.lowerBound == 0.0:
      self._distribution = distribution1D.BasicWeibullDistribution(self.k,self.lambda_var)
    else:
      if self.lowerBoundUsed == False:
        a = 0.0
        self.lowerBound = a
      else:a = self.lowerBound
      if self.upperBoundUsed == False:
        b = sys.float_info.max
        self.upperBound = b
      else:b = self.upperBound
      self._distribution = distribution1D.BasicWeibullDistribution(self.k,self.lambda_var,a,b)


class NDimensionalDistributions(Distribution): # pragma: under development
  def __init__(self):
    Distribution.__init__(self)
    self.data_filename = None
    self.function_type = None
    self.type = 'NDimensionalDistributions'
    self.dimensionality  = 'ND'
  def _readMoreXML(self,xmlNode):
    Distribution._readMoreXML(self, xmlNode)
    data_filename = xmlNode.find('data_filename')
    if data_filename != None: self.data_filename = data_filename.text
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> <data_filename> parameter needed for MultiDimensional Distributions!!!!')
    function_type = xmlNode.find('function_type')
    if not function_type: self.function_type = 'CDF'
    else:
      self.function_type = function_type.upper()
      if self.function_type not in ['CDF','PDF']:  raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> <function_type> parameter needs to be either CDF or PDF in MultiDimensional Distributions!!!!')
  def addInitParams(self,tempDict):
    Distribution.addInitParams(self, tempDict)
    tempDict['function_type'] = self.function_type
    tempDict['data_filename'] = self.data_filename


class NDInverseWeight(NDimensionalDistributions): # pragma: under development
  def __init__(self):
    NDimensionalDistributions.__init__(self)
    self.p  = None
    self.type = 'NDInverseWeight'

  def _readMoreXML(self,xmlNode):
    NDimensionalDistributions._readMoreXML(self, xmlNode)
    self.p = xmlNode.find('p')
    if self.p != None: self.p = float(self.p)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> Minkowski distance parameter <p> not found in NDInverseWeight distribution')
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    NDimensionalDistributions.addInitParams(self, tempDict)
    tempDict['p'] = self.p

  def initializeDistribution(self):
    NDimensionalDistributions.initializeDistribution()
    self._distribution = distribution1D.BasicMultiDimensionalInverseWeight(self.p)

  def cdf(self,x):
    return self._distribution.Cdf(x)

  def ppf(self,x):
    return self._distribution.InverseCdf(x)

  def pdf(self,x):
    return self._distribution.Pdf(x)

  def untruncatedCdfComplement(self, x):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedCdfComplement not yet implemented for ' + self.type)

  def untruncatedHazard(self, x):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedHazard not yet implemented for ' + self.type)

  def untruncatedMean(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMean not yet implemented for ' + self.type)

  def untruncatedMedian(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMedian not yet implemented for ' + self.type)

  def untruncatedMode(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMode not yet implemented for ' + self.type)

  def rvs(self,*args):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> rvs not yet implemented for ' + self.type)


class NDScatteredMS(NDimensionalDistributions): # pragma: under development
  def __init__(self):
    NDimensionalDistributions.__init__(self)
    self.p  = None
    self.precision = None
    self.type = 'NDScatteredMS'

  def _readMoreXML(self,xmlNode):
    NDimensionalDistributions._readMoreXML(self, xmlNode)
    self.p = xmlNode.find('p')
    if self.p != None: self.p = float(self.p)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> Minkowski distance parameter <p> not found in NDScatteredMS distribution')
    self.precision = xmlNode.find('precision')
    if self.precision != None: self.precision = float(self.precision)
    else: raise Exception(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> precision parameter <precision> not found in NDScatteredMS distribution')
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    NDimensionalDistributions.addInitParams(self, tempDict)
    tempDict['p'] = self.p
    tempDict['precision'] = self.precision

  def initializeDistribution(self):
    NDimensionalDistributions.initializeDistribution()
    self._distribution = distribution1D.BasicMultiDimensionalScatteredMS(self.p,self.precision)

  def cdf(self,x):
    return self._distribution.Cdf(x)

  def ppf(self,x):
    return self._distribution.InverseCdf(x)

  def pdf(self,x):
    return self._distribution.Pdf(x)

  def untruncatedCdfComplement(self, x):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedCdfComplement not yet implemented for ' + self.type)

  def untruncatedHazard(self, x):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedHazard not yet implemented for ' + self.type)

  def untruncatedMean(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMean not yet implemented for ' + self.type)

  def untruncatedMedian(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMedian not yet implemented for ' + self.type)

  def untruncatedMode(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMode not yet implemented for ' + self.type)

  def rvs(self,*args):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> rvs not yet implemented for ' + self.type)


class NDCartesianSpline(NDimensionalDistributions): # pragma: under development
  def __init__(self):
    NDimensionalDistributions.__init__(self)
    self.type = 'NDCartesianSpline'

  def _readMoreXML(self,xmlNode):
    NDimensionalDistributions._readMoreXML(self, xmlNode)
    self.initializeDistribution()

  def addInitParams(self,tempDict):
    NDimensionalDistributions.addInitParams(self, tempDict)

  def initializeDistribution(self):
    NDimensionalDistributions.initializeDistribution()
    self._distribution = distribution1D.BasicMultiDimensionalCartesianSpline()

  def cdf(self,x):
    return self._distribution.Cdf(x)

  def ppf(self,x):
    return self._distribution.InverseCdf(x)

  def pdf(self,x):
    return self._distribution.Pdf(x)

  def untruncatedCdfComplement(self, x):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedCdfComplement not yet implemented for ' + self.type)

  def untruncatedHazard(self, x):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedHazard not yet implemented for ' + self.type)

  def untruncatedMean(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMean not yet implemented for ' + self.type)

  def untruncatedMedian(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMedian not yet implemented for ' + self.type)

  def untruncatedMode(self):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> untruncatedMode not yet implemented for ' + self.type)

  def rvs(self,*args):
    raise NotImplementedError(self.printTag+': ' +returnPrintPostTag('ERROR') + '-> rvs not yet implemented for ' + self.type)


__base                        = 'Distribution'
__interFaceDict               = {}
__interFaceDict['Uniform'          ] = Uniform
__interFaceDict['Normal'           ] = Normal
__interFaceDict['Gamma'            ] = Gamma
__interFaceDict['Beta'             ] = Beta
__interFaceDict['Triangular'       ] = Triangular
__interFaceDict['Poisson'          ] = Poisson
__interFaceDict['Binomial'         ] = Binomial
__interFaceDict['Bernoulli'        ] = Bernoulli
__interFaceDict['Logistic'         ] = Logistic
__interFaceDict['Exponential'      ] = Exponential
__interFaceDict['LogNormal'        ] = LogNormal
__interFaceDict['Weibull'          ] = Weibull
__interFaceDict['NDInverseWeight'  ] = NDInverseWeight
__interFaceDict['NDScatteredMS'    ] = NDScatteredMS
__interFaceDict['NDCartesianSpline'] = NDCartesianSpline
__knownTypes                  = __interFaceDict.keys()

def knownTypes():
  return __knownTypes

def returnInstance(Type):
  try: return __interFaceDict[Type]()
  except KeyError: raise NameError('not known '+__base+' type '+Type)
