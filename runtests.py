import os
import sys
import yaml
import contextlib
from datetime import datetime


@contextlib.contextmanager
def working_directory(path):
    """A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.

    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def find_tests(tests_dir):
    for fname in os.listdir(tests_dir):
        if not fname.endswith('.test.yaml'):
            continue
        fpath = os.path.join(tests_dir, fname)
        with open(fpath) as fp:
            yield yaml.load(fp)


def run_test(test, cmd_prefix, tests_dir):
    app = tests_dir+''+test['app']
    inputs = tests_dir+test['inputs']
    expected = test['expected']
    cmd = '%s %s %s > result.yaml' % (cmd_prefix, app, inputs)
    print('Running cmd: %s' % cmd)
    return_code = os.system(cmd)
    print('Return code: %s' % return_code)
    if return_code:
        return False
    with open('result.yaml') as fp:
        result = yaml.load(fp)
    print('Result:\n%s\nExpected:\n%s' % (result, expected))
    sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S - ')
    resStr = str(result)
    expStr = str(expected)
    with open("TestLog.log", "a") as myfile:
        myfile.write('\n'+sttime)
        myfile.write('\n'+resStr)
        myfile.write('\n'+expStr)
    return relative_paths(result) == expected


def relative_paths(o):
    if isinstance(o, dict) and o.get('class') == 'File':
        return {'class': 'File', 'name': o.get('path').split('/')[-1], 'size': o.get('size')}
    if isinstance(o, dict):
        return {k: relative_paths(v) for k, v in o.items()}
    if isinstance(o, list):
        return [relative_paths(i) for i in o]
    return o


def main():
    tests_dir = sys.argv[1]
    cmd_prefix = sys.argv[2]
    for suite in find_tests(tests_dir):
        for test_name, test in suite.items(): #kako je mapiran test_name u fajlu? kako on zna da je test_name bas test1, test2,itd...
            print('Running test %s' % test_name)
            with working_directory(tests_dir):
                run_test(test, cmd_prefix, tests_dir)


if __name__ == '__main__':
    main()
