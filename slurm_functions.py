import os


def get_script_bootstrap_slave():
    script_path = os.path.dirname(os.path.abspath(__file__)) + '/bootstrap_portfolio_slave.py'
    return script_path

