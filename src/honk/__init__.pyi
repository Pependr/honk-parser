from typing import Any, Mapping, Callable, Sequence

type NestedData = Mapping[str, Any] | Sequence[Any]
type ParseStrat = Callable[[str], NestedData]

def parser(ext: str) -> Callable[[ParseStrat], ParseStrat]: ...
def template[T](
    *args: Any, **kwargs: Any
) -> Callable[[Callable[..., T]], Callable[..., T]]: ...
