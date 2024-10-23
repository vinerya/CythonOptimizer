import os
import shutil
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def integrate_with_ci_cd(optimized_files: Dict[str, str], output_path: str):
    os.makedirs(output_path, exist_ok=True)
    
    for file_path, content in optimized_files.items():
        relative_path = os.path.relpath(file_path)
        output_file_path = os.path.join(output_path, relative_path)
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        
        # Copy the compiled .so or .pyd file instead of writing the content
        compiled_file = file_path.replace('.py', '.cpython-*').replace('.pyx', '.cpython-*')
        compiled_files = [f for f in os.listdir(os.path.dirname(file_path)) if f.startswith(os.path.basename(compiled_file))]
        
        if compiled_files:
            compiled_file_path = os.path.join(os.path.dirname(file_path), compiled_files[0])
            output_compiled_path = output_file_path.replace('.py', '.pyd' if os.name == 'nt' else '.so')
            try:
                shutil.copy2(compiled_file_path, output_compiled_path)
                logger.info(f"Copied optimized module: {output_compiled_path}")
            except Exception as e:
                logger.error(f"Failed to copy compiled file {compiled_file_path}: {str(e)}")
                # Fall back to the original Python file
                with open(output_file_path, 'w') as f:
                    f.write(content)
                logger.info(f"Fell back to original Python file: {output_file_path}")
        else:
            # If compilation failed, fall back to the original Python file
            with open(output_file_path, 'w') as f:
                f.write(content)
            logger.info(f"No compiled file found, using original Python file: {output_file_path}")
    
    # Copy necessary files (e.g., setup.py, README.md) to the output directory
    shutil.copy2('setup.py', output_path)
    shutil.copy2('README.md', output_path)

    logger.info(f"Optimized package created at: {output_path}")
    logger.info("You can now include this directory in your CI/CD pipeline for further processing or deployment.")