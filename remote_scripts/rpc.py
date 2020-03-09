from typing import Any, Dict

import functions
from util import log


def call(method_name: str, *args: Any) -> Dict[str, Any]:
    log(method_name)
    method = getattr(functions, method_name)  # TODO: type method instead of result
    result: Dict[str, Any] = method(*args)
    return result
