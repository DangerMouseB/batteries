#*******************************************************************************
#
#    Copyright (c) 2020 David Briant
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#*******************************************************************************


from ..pipeable import Pipeable



class NamedEnum(object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return '%s(\'%s\')' % (self.__class__.__name__, self.name)
    def __str__(self):
        return self.name


class ObserversCtx(NamedEnum):pass



_FpMLCityByName = {}
class FpMLCity(ObserversCtx):
    def __init__(self, name):
        super().__init__(name)
        _FpMLCityByName[name] = self
# see https://www.fpml.org/spec/coding-scheme/fpml-schemes.html#s5.16
# TODO load from XML config
FpMLCity.AUSY = FpMLCity('AUSY')    # Sydney, Australia
FpMLCity.CATO = FpMLCity('CATO')    # Toronto, Canada
FpMLCity.CHZU = FpMLCity('CHZU')    # Zurich, Switzerland
FpMLCity.CNBE = FpMLCity('CNBE')    # Beijing, China
FpMLCity.DEFR = FpMLCity('DEFR')    # Frankfurt, Germany
FpMLCity.ESMA = FpMLCity('ESMA')    # Madrid, Spain
FpMLCity.FRPA = FpMLCity('FRPA')    # Paris, France
FpMLCity.GBLO = FpMLCity('GBED')    # London, Edinburgh
FpMLCity.GBLO = FpMLCity('GBLO')    # London, United Kingdom
FpMLCity.GRAT = FpMLCity('GRAT')    # Athens, Greece
FpMLCity.HKHK = FpMLCity('HKHK')    # Hong Kong, Hong Kong
FpMLCity.ITMI = FpMLCity('ITMI')    # Milan, Italy
FpMLCity.JPTO = FpMLCity('JPTO')    # Tokyo, Japan
FpMLCity.KRSE = FpMLCity('KRSE')    # Seoul, Republic of Korea
FpMLCity.MYKL = FpMLCity('MYKL')    # Kuala Lumpur, Malaysia
FpMLCity.RUMO = FpMLCity('RUMO')    # Moscow, Russian Federation
FpMLCity.SGSI = FpMLCity('SGSI')    # Singapore, Singapore
FpMLCity.USCH = FpMLCity('USCH')    # Chicago, United States
FpMLCity.USDC = FpMLCity('USDC')    # Washington, District of Columbia, United States
FpMLCity.USNY = FpMLCity('USNY')    # New York, United States
def FpMLCityForName(name):
    return _FpMLCityByName[name]



_IanaCityByName = {}
class IanaCity(ObserversCtx):
    def __init__(self, name):
        super().__init__(name)
        _IanaCityByName[name] = self
# TODO load from Iana database
IanaCity.Europe_London = IanaCity('Europe/London')
IanaCity.Europe_Paris = IanaCity('Europe/Paris')
IanaCity.America_New_York = IanaCity('America/New_York')
IanaCity.Asia_Hong_Kong = IanaCity('Asia/Hong_Kong')
def IanaCityForName(name):
    return _IanaCityByName[name]



_IanaTzByName = {}
class IanaTz(ObserversCtx):
    def __init__(self, name):
        super().__init__(name)
        _IanaTzByName[name] = self
# TODO load from Iana database
IanaTz.BST = IanaTz('BST')
IanaTz.GMT = IanaTz('GMT')
IanaTz.GMT = IanaTz('EST')
IanaTz.GMT = IanaTz('ESD')
def IanaTzForName(name):
    return _IanaTzByName[name]



_IanaCityByFpMLCity= dict(
    GBLO = IanaCity.Europe_London,
    GBED = IanaCity.Europe_London,
    USDC = IanaCity.America_New_York,
    USNY = IanaCity.America_New_York
)
@Pipeable
def ToIanaCity(fpmlCity):
    return _IanaCityByFpMLCity[fpmlCity]



class Precision(NamedEnum): pass
Precision.s = Precision('s')
Precision.ms = Precision('ms')
Precision.us = Precision('us')
Precision.ns = Precision('ns')

