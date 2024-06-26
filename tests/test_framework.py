from dataclasses import dataclass
from uuid import UUID, uuid4

from result import Err, Ok, Result
import recursive_handlers


@dataclass(frozen=True)
class CreateAccountParam(recursive_handlers.InputParams):
    initial_balance: int


@dataclass(frozen=True)
class CreateAccountOut(recursive_handlers.Output):
    account_id: UUID


class NegativeOrZeroInitialBalanceError(recursive_handlers.DomainError):
    def __init__(self) -> None:
        super().__init__(
            "Not possible to open an account with a negative or zero initial balance."
        )


class ZeroInitialBalanceError(recursive_handlers.DomainError):
    def __init__(self) -> None:
        super().__init__(
            "Not possible to open an account with a negative or zero initial balance."
        )


@dataclass(frozen=True)
class AccountCreated(recursive_handlers.DomainEvent):
    account_id: UUID

    async def publish(self) -> None: ...


async def _async_create_account(
    domain_events: list[recursive_handlers.DomainEvent],
    params: CreateAccountParam,
) -> Result[CreateAccountOut, NegativeOrZeroInitialBalanceError]:
    if params.initial_balance <= 0:
        return Err(NegativeOrZeroInitialBalanceError())
    account_id = uuid4()
    domain_events.append(AccountCreated(account_id=account_id))
    return Ok(CreateAccountOut(account_id=account_id))


# Railway
def _create_account(
    domain_events: list[recursive_handlers.DomainEvent],
    params: CreateAccountParam,
) -> Result[
    CreateAccountOut, NegativeOrZeroInitialBalanceError | ZeroInitialBalanceError
]:
    if params.initial_balance <= 0:
        return Err(NegativeOrZeroInitialBalanceError())
    account_id = uuid4()
    domain_events.append(AccountCreated(account_id=account_id))
    return Ok(CreateAccountOut(account_id=account_id))


async def test_run_handler() -> None:
    account_created_result = await recursive_handlers.run(
        handler=_create_account, params=CreateAccountParam(initial_balance=10_000)
    )
    assert isinstance(account_created_result, Ok)
    domain_events, account_created = account_created_result.unwrap()
    assert domain_events == [AccountCreated(account_created.account_id)]
    assert account_created == CreateAccountOut(account_id=account_created.account_id)


async def test_run_handler_with_error() -> None:
    account_created_result = await recursive_handlers.run(
        handler=_create_account, params=CreateAccountParam(initial_balance=-10_000)
    )
    assert isinstance(account_created_result, Err)
    domain_error = account_created_result.err()
    assert isinstance(domain_error, NegativeOrZeroInitialBalanceError)


async def test_run_async_handler() -> None:
    account_created_result = await recursive_handlers.run(
        handler=_async_create_account, params=CreateAccountParam(initial_balance=10_000)
    )
    assert isinstance(account_created_result, Ok)
    domain_events, account_created = account_created_result.unwrap()
    assert domain_events == [AccountCreated(account_created.account_id)]
    assert account_created == CreateAccountOut(account_id=account_created.account_id)
