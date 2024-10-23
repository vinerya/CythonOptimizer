import argparse
import sys
import logging
from optimizer import CythonOptimizer
from ci_cd_integration import integrate_with_ci_cd

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="CythonOptimizer: Optimize Python projects by selectively cythonizing parts of the codebase.")
    parser.add_argument("project_path", help="Path to the Python project to optimize")
    parser.add_argument("--output", help="Path to store the optimized package", default="optimized_output")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parsed_args = parser.parse_args(args)

    if parsed_args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    optimizer = CythonOptimizer(parsed_args.project_path, debug=parsed_args.debug)
    optimized_files = optimizer.optimize()
    
    integrate_with_ci_cd(optimized_files, parsed_args.output)

if __name__ == "__main__":
    main()