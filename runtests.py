import os
import sys
import yaml
import contextlib
from datetime import datetime

# Taken from http://stackoverflow.com/a/21048064
# _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
# def dict_representer(dumper, data):
#     return dumper.represent_dict(data.items())
# def dict_constructor(loader, node):
#     return collections.OrderedDict(loader.construct_pairs(node))
# yaml.add_representer(collections.OrderedDict, dict_representer)
# yaml.add_constructor(_mapping_tag, dict_constructor)


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


def run_test(test, cmd_prefix, tests_dir, test_name):
    app = test['app']
    inputs = test['inputs']
    expected = test['expected']
    cmd = '%s -e . %s %s > result.yaml' % (cmd_prefix, app, inputs)
    print('Running cmd: %s' % cmd)
    return_code = os.system(cmd)
    print('Return code: %s' % return_code)
    if return_code:
        return False
    with open('result.yaml') as fp:
        result = yaml.load(fp)
    print('Result:\n%s\nExpected:\n%s' % (result, expected))
    sttime = datetime.now().strftime('%Y%m%d_%H:%M:%S')
    resStr = str(result)
    expStr = str(expected)
    retCod = str(return_code)
    with open("TestLog"+sttime+".log", "a") as myfile:
        myfile.write('test name: '+test_name+'\n')
        # myfile.write('\n\ttimestamp: '+sttime)
        myfile.write('\tResult: '+resStr+'\n')
        myfile.write('\tExpected: '+expStr+'\n')
        myfile.write('\tReturn code: '+retCod+'\n')
        # cmpVal = compare_expected_result(result,expected)
        print('Result after relative paths: %s' % relative_paths(result))
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
    passed = True
    for suite in find_tests(tests_dir):
        for test_name, test in suite.items():
            print('Running test %s' % test_name)
            with working_directory('.'):  #tests_dir):
                returned_from_RT = run_test(test, cmd_prefix, tests_dir, test_name)
                print('Returned from run test method: '+str(returned_from_RT))
                if not returned_from_RT:
                    passed = False
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
