from abc import ABC, abstractmethod
from collections.abc import Coroutine
from typing import Any, Callable, TypeVar
from typing_extensions import assert_never

from result import Result, Err, Ok


class InputParams: ...


In = TypeVar("In", bound=InputParams)


class Output: ...


Out = TypeVar("Out", bound=Output)


class DomainEvent(ABC):
    @abstractmethod
    async def publish(self) -> None:
        raise NotImplementedError


class DomainError(Exception): ...


DomErr = TypeVar("DomErr", bound=DomainError)


async def run_and_collect_events(
    handler: Callable[[list[DomainEvent], In], Result[Out, DomErr]]
    | Callable[[list[DomainEvent], In], Coroutine[Any, Any, Result[Out, DomErr]]],
    params: In,
) -> Result[tuple[list[DomainEvent], Out], DomErr]:
    domain_events: list[DomainEvent] = []
    handler_result_or_coroutine = handler(domain_events, params)
    match handler_result_or_coroutine:
        case Coroutine():
            handler_result = await handler_result_or_coroutine
        case _:
            handler_result = handler_result_or_coroutine

    match handler_result:
        case Err(domain_error):
            return Err(domain_error)
        case Ok(output):
            return Ok((domain_events, output))
        case _:
            assert_never(handler_result)
