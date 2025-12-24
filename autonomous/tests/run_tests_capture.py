import sys
import pytest

def main():
    # run pytest and capture the result to an output file
    out_path = 'services/real-estate-intelligence/autonomous/tests/test_run_output.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        # run tests in this directory
        # pytest.main writes to stdout; capture by redirecting sys.stdout
        orig_stdout = sys.stdout
        try:
            sys.stdout = f
            ret = pytest.main(['-q', 'services/real-estate-intelligence/autonomous/tests'])
        finally:
            sys.stdout = orig_stdout
    print('pytest finished, output written to', out_path)

if __name__ == '__main__':
    main()
