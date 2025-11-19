import sympy as sp

class NewtonRaphsonModel:
    def __init__(self):
        self.x = sp.symbols('x')

    def solve(self, func_str, initial_guess, tolerance=1e-6, max_iter=50):
        """
        Solves for the root using Newton-Raphson method.
        Returns a dictionary with 'root', 'converged', and 'history'.
        """
        history = []

        try:
            # 1. Parse the function string into a SymPy expression
            # We restrict locals to math functions for safety
            func_expr = sp.sympify(func_str)

            # 2. Calculate the derivative symbolically
            deriv_expr = sp.diff(func_expr, self.x)

            # Convert to efficient python functions for numerical calculation
            f = sp.lambdify(self.x, func_expr, 'math')
            df = sp.lambdify(self.x, deriv_expr, 'math')

            x_n = float(initial_guess)

            for i in range(max_iter):
                f_val = f(x_n)
                df_val = df(x_n)

                # Record history
                history.append({
                    'iteration': i + 1,
                    'x_n': x_n,
                    'f_x': f_val,
                    'df_x': df_val
                })

                # Check for convergence (if f(x) is close enough to 0)
                if abs(f_val) < tolerance:
                    return {
                        'root': x_n,
                        'converged': True,
                        'history': history,
                        'message': "Converged within tolerance."
                    }

                # Check for division by zero (derivative is 0)
                if df_val == 0:
                    return {
                        'root': None,
                        'converged': False,
                        'history': history,
                        'message': "Error: Derivative is zero. No solution found."
                    }

                # Newton-Raphson Formula: x(n+1) = x(n) - f(x) / f'(x)
                x_n = x_n - (f_val / df_val)

            return {
                'root': x_n,
                'converged': False,
                'history': history,
                'message': "Max iterations reached without full convergence."
            }

        except Exception as e:
            return {'error': str(e)}