from typing import Sequence

import libcst

from fenec.python_parser.model_builders.function_model_builder import (
    FunctionModelBuilder,
)

from fenec.models.models import (
    DecoratorModel,
    ParameterListModel,
    # ParameterModel,
)
from fenec.models.enums import BlockType
import fenec.python_parser.visitors.node_processing.common_functions as common_functions

from fenec.utilities.processing_context import PositionData


def process_func_def(
    func_id: str,
    node: libcst.FunctionDef,
    position_data: PositionData,
    func_builder: FunctionModelBuilder,
) -> None:
    """
    Processes a libcst.FunctionDef node to build a function model.

    Extracts various components of a function definition such as its docstring, code content, decorators, and return annotations,
    and updates the provided FunctionModelBuilder with these details.

    Args:
        - func_id (str): The unique identifier for the function.
        - node (libcst.FunctionDef): The function definition node from the CST.
        - position_data (PositionData): Positional data for the function in the source code.
        - func_builder (FunctionModelBuilder): The builder used to construct the function model.

    Example:
        ```Python
        func_builder = FunctionModelBuilder(id="func1", ...)
        process_func_def("func1", function_node, position_data, func_builder)
        # Processes the function definition and updates the function builder.
        ```
    """

    docstring: str | None = node.get_docstring()
    code_content: str = common_functions.extract_code_content(node)
    decorators: list[DecoratorModel] | None = common_functions.extract_decorators(
        node.decorators
    )

    returns: str = (
        _extract_return_annotation(node.returns)
        if node.returns
        else "Function has no return annotation"
    )
    (
        func_builder.set_docstring(docstring)
        .set_code_content(code_content)
        .set_start_line_num(position_data.start)
        .set_end_line_num(position_data.end)
    )
    (
        func_builder.set_decorators(decorators)
        .set_is_method(_func_is_method(func_id))
        .set_is_async(_func_is_async(node))
        .set_return_annotation(returns)
    )


def process_parameters(
    node: libcst.Parameters,
) -> ParameterListModel | None:
    """
    Processes libcst.Parameters node to create a ParameterListModel.

    Extracts parameters, keyword-only parameters, positional-only parameters, and special arguments (like *args and **kwargs)
    from the function definition and forms a model representing these parameters.

    Args:
        - node (libcst.Parameters): The parameters node from a function definition.

    Returns:
        - ParameterListModel | None: A model representing the function's parameters, or None if there are no parameters.

    Example:
        ```Python
        parameters_model = process_parameters(function_node.params)
        # Processes the function parameters and returns a parameter model.
        ```
    """

    # params: list[ParameterModel] | None = (
    #     _get_parameters_list(node.params) if node.params else []
    # )
    params: list[str] | None = (
        _get_parameters_list(node.params) if node.params else None
    )

    # kwonly_params: list[ParameterModel] | None = (
    #     _get_parameters_list(node.kwonly_params) if node.kwonly_params else []
    # )
    # posonly_params: list[ParameterModel] | None = (
    #     _get_parameters_list(node.posonly_params) if node.posonly_params else []
    # )

    # star_arg: ParameterModel | None = (
    #     ParameterModel(
    #         content=common_functions.extract_stripped_code_content(node.star_arg)
    #     )
    #     if node.star_arg and isinstance(node.star_arg, libcst.Param)
    #     else None
    # )
    # star_kwarg: ParameterModel | None = (
    #     ParameterModel(
    #         content=common_functions.extract_stripped_code_content(node.star_kwarg)
    #     )
    #     if node.star_kwarg
    #     else None
    # )
    kwonly_params: list[str] | None = (
        _get_parameters_list(node.kwonly_params) if node.kwonly_params else None
    )
    posonly_params: list[str] | None = (
        _get_parameters_list(node.posonly_params) if node.posonly_params else None
    )

    star_arg: str | None = (
        common_functions.extract_stripped_code_content(node.star_arg)
        if node.star_arg and isinstance(node.star_arg, libcst.Param)
        else None
    )
    star_kwarg: str | None = (
        common_functions.extract_stripped_code_content(node.star_kwarg)
        if node.star_kwarg
        else None
    )

    if params and kwonly_params and posonly_params and star_arg and star_kwarg:
        return ParameterListModel(
            params=params,
            kwonly_params=kwonly_params,
            posonly_params=posonly_params,
            star_arg=star_arg,
            star_kwarg=star_kwarg,
        )


def _func_is_method(id: str) -> bool:
    """
    Returns true if an ancestor of the function is a class.

    Args:
        - id (str): The identifier of the function.

    Returns:
        - bool: True if the function is a method, False otherwise.
    """

    return str(BlockType.CLASS) in id


def _func_is_async(node: libcst.FunctionDef) -> bool:
    """
    Returns true if the function is async.

    Args:
        - node (libcst.FunctionDef): The function definition node.

    Returns:
        - bool: True if the function is async, False otherwise.
    """

    return True if node.asynchronous else False


def _get_parameters_list(
    parameter_sequence: Sequence[libcst.Param],
    # ) -> list[ParameterModel] | None:
) -> list[str] | None:
    # """
    # Returns a list of ParameterModel representing the parameters in a function definition.

    # Args:
    #     - parameter_sequence (Sequence[libcst.Param]): The sequence of parameters from the function definition.

    # Returns:
    #     - list[ParameterModel] | None: A list of ParameterModel instances or None if there are no parameters.
    # """
    """
    Returns a list of strings representing the parameters in a function definition.

    Args:
        - `parameter_sequence` (Sequence[libcst.Param]): The sequence of parameters from the function definition.

    Returns:
        - `list[str] | None`: A list of strings or None if there are no parameters.
    """

    # params: list[ParameterModel] | None = None
    params: list[str] | None = None

    if parameter_sequence:
        params = []
        for parameter in parameter_sequence:
            # param: ParameterModel = ParameterModel(
            # content=common_functions.extract_stripped_code_content(parameter)
            # )
            param = common_functions.extract_stripped_code_content(parameter)
            params.append(param)

    return params if params else None


def _extract_return_annotation(
    node_returns: libcst.Annotation | None,
) -> str:
    """ "
    Extracts the return annotation from a function definition.

    Args:
        - node_returns (libcst.Annotation | None): The return annotation node.

    Returns:
        - str: The extracted return annotation or "No return annotation" if none is found.
    """

    if isinstance(node_returns, libcst.Annotation) and node_returns:
        annotation: str | None = common_functions.extract_type_annotation(node_returns)
        return annotation if annotation else "No return annotation"
    else:
        return "No return annotation"
