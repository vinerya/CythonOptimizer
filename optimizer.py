import os
import ast
from typing import List, Dict
import Cython.Build.Cythonize as cythonize
import Cython.Compiler.Options
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Cython.Compiler.Options.annotate = True

class CythonOptimizer:
    def __init__(self, project_path: str, debug: bool = False):
        self.project_path = project_path
        self.debug = debug

    def optimize(self) -> Dict[str, str]:
        optimized_files = {}
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        optimized_content = self._optimize_file(file_path)
                        if optimized_content:
                            optimized_files[file_path] = optimized_content
                    except Exception as e:
                        logger.error(f"Failed to optimize {file_path}: {str(e)}", exc_info=True)
        return optimized_files

    def _optimize_file(self, file_path: str) -> str:
        with open(file_path, 'r') as f:
            content = f.read()
        
        try:
            tree = ast.parse(content)
            transformer = _CythonTransformer()
            cython_tree = transformer.visit(tree)
            
            # Generate Cython code
            cython_content = self._generate_cython_code(cython_tree)
            
            if self.debug:
                logger.debug(f"Generated Cython code for {file_path}:\n{cython_content}")
            
            # Save Cython code to .pyx file
            pyx_file = file_path.replace('.py', '.pyx')
            with open(pyx_file, 'w') as f:
                f.write(cython_content)
            
            # Compile Cython code
            compile_result = cythonize(
                pyx_file,
                compiler_directives={
                    'language_level': 3,
                    'boundscheck': False,
                    'wraparound': False,
                    'nonecheck': False,
                },
                include_path=[np.get_include()],
                force=True
            )
            
            if not compile_result:
                raise Exception("Cython compilation failed")
            
            logger.info(f"Successfully optimized {file_path}")
            
            return cython_content
        except Exception as e:
            logger.error(f"Error during optimization of {file_path}: {str(e)}", exc_info=True)
            raise

    def _generate_cython_code(self, tree: ast.AST) -> str:
        cython_code = "# distutils: language=c++\n"
        cython_code += "# cython: language_level=3\n"
        cython_code += "# cython: boundscheck=False, wraparound=False, nonecheck=False\n"
        cython_code += "cimport cython\n"
        cython_code += "import numpy as np\n"
        cython_code += "cimport numpy as np\n\n"
        cython_code += "np.import_array()\n\n"
        
        for node in tree.body:
            if isinstance(node, ast.Import):
                cython_code += ast.unparse(node) + "\n"
            elif isinstance(node, ast.ImportFrom):
                cython_code += ast.unparse(node) + "\n"
            elif isinstance(node, ast.FunctionDef):
                cython_code += ast.unparse(node) + "\n\n"
            else:
                cython_code += ast.unparse(node) + "\n"
        
        return cython_code

class _CythonTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # Convert Python function definitions to Cython cdef functions
        cdef_decorator = any(decorator.id == 'cython.ccall' for decorator in node.decorator_list if isinstance(decorator, ast.Name))
        
        func_type = "cdef" if cdef_decorator else "cpdef"
        return_type = "object"
        if node.returns:
            return_type = getattr(node.returns, 'id', 'object')
        
        # Create a new function definition
        new_node = ast.FunctionDef(
            name=node.name,
            args=self._transform_arguments(node.args),
            body=node.body,
            decorator_list=[],
            returns=None
        )
        
        # Add Cython function type and return type
        new_node.body.insert(0, ast.Expr(ast.Str(f"{func_type} {return_type}")))
        
        # Copy all attributes from the original node
        ast.copy_location(new_node, node)
        
        return new_node

    def _transform_arguments(self, args):
        new_args = ast.arguments(
            posonlyargs=[],
            args=[],
            vararg=args.vararg,
            kwonlyargs=args.kwonlyargs,
            kw_defaults=args.kw_defaults,
            kwarg=args.kwarg,
            defaults=args.defaults
        )
        
        for arg in args.args:
            if arg.annotation:
                arg_type = getattr(arg.annotation, 'id', 'object')
                new_arg = ast.arg(arg=f"{arg_type} {arg.arg}", annotation=None)
            else:
                new_arg = ast.arg(arg=arg.arg, annotation=None)
            ast.copy_location(new_arg, arg)
            new_args.args.append(new_arg)
        
        return new_args

    def visit_For(self, node):
        # Optimize range-based loops
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
            node.iter = ast.Call(
                func=ast.Name(id='cython.parallel.prange', ctx=ast.Load()),
                args=node.iter.args,
                keywords=[]
            )
        return node

# Add more optimization methods as needed