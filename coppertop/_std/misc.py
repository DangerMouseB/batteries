#*******************************************************************************
#
#    Copyright (c) 2017-2020 David Briant
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



from coppertop.pipeable import Pipeable


# conversions

@Pipeable
def ToStr(x):
    return str(x)

@Pipeable
def ToInt(a):
    return int(a)


# other

@Pipeable
def Not(x):
    return not x




@Pipeable
def GetAttr(x, name):
    return getattr(x, name)




