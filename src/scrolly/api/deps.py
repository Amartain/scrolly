from collections.abc import Iterator

from fastapi import Request

from scrolly.ports import Clock, Store


def get_clock(request: Request) -> Clock:
    clock: Clock = request.app.state.clock
    return clock


def get_store(request: Request) -> Iterator[Store]:
    with request.app.state.store_factory() as store:
        yield store
