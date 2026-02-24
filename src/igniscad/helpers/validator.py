import functools
import inspect
import math
from types import SimpleNamespace

from igniscad.helpers.constants import TOLERANCE
from igniscad.helpers.exceptions import InfeasibleEntityError


def validate_dimensions(*args_to_check: str):
    """
    Validate whether the specified dimensions are strictly positive (> 0).
    Raises InfeasibleEntityError if <= 0.

    Args:
        args_to_check(str): the arguments to validate
    """

    def decorator(func):
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            params = bound_args.arguments

            invalid_params = []
            for arg_name in args_to_check:
                if arg_name in params:
                    val = params[arg_name]
                    
                    if val <= TOLERANCE:
                        invalid_params.append(f"{arg_name}={val}")

            if invalid_params:
                func_name = func.__name__
                provided_name = params.get("name")

                display_name = provided_name if provided_name else f"{func_name}<Pending>"
                error_detail = ", ".join(invalid_params)
                raise InfeasibleEntityError(
                    entity=SimpleNamespace(name=display_name),
                    reason=f"Dimensions must be positive. Invalid arguments: {error_detail}"
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_vertices(arg_name: str = "points", min_points=3):
    """
    Validator for vertices / points.
    Validate the vertex count and the coincidence (distance between adjacent vertices).

    Args:
        arg_name(str): the argument to check.
        min_points(int): the smallest count of points.
    """

    def decorator(func):
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            params = bound_args.arguments

            points = params.get(arg_name)


            if not points:
                raise InfeasibleEntityError(
                    entity=SimpleNamespace(name=f"{func.__name__}<Pending>"),
                    reason="No vertices provided."
                )

            if len(points) < min_points:
                raise InfeasibleEntityError(
                    entity=SimpleNamespace(name=f"{func.__name__}<Pending>"),
                    reason=f"Polygon requires at least {min_points} vertices. Got {len(points)}."
                )

            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]

                dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

                if dist <= TOLERANCE:
                    raise InfeasibleEntityError(
                        entity=SimpleNamespace(name=f"{func.__name__}<Pending>"),
                        reason=(
                            f"Vertex {i} {p1} and Vertex {(i + 1) % len(points)} {p2} are too close "
                            f"(distance {dist:.2e} < tolerance {TOLERANCE}). "
                            "This would create a zero-length edge."
                        )
                    )

            return func(*args, **kwargs)

        return wrapper

    return decorator