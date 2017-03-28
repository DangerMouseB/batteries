#*******************************************************************************
#
#    Copyright (c) 2011-2012 David Briant
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


if __name__ == '__main__':
    import sys
    from testconfig import config    
    stdout, stdin = sys.stdout, sys.stdin
    config['argv'] = sys.argv
    config['stdout'] = stdout
    sys.argv = [arg for arg in sys.argv if arg[:1] != "/"]
    try:
        from nose import main
        main(exit=True)     # exit=True cause a SystemExit to be thrown at the end (this is default behaviour)
    except SystemExit:
        sys.stdout = stdout
        et, ev, tb = sys.exc_info()
        if "/WAIT" in [arg.upper() for arg in config['argv']]:
            stdout.write("Press Enter to continue...")
            stdin.readline()
        raise ev



