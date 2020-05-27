# *******************************************************************************

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
# *******************************************************************************



from ..pipeable import Pipeable


# Composition - could be made more efficient

@Pipeable(overrideLHS=True)
def Compose(f1, f2):
    @Pipeable
    def _Composed(x):
        return x >> f1 >> f2
    return _Composed

@Pipeable(overrideLHS=True)
def ComposeAll(f1, f2):
    raise NotImplementedError()
