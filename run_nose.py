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



