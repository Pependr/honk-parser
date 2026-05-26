import click

import functools

from typing import Any, Callable

from mdparser import main


def template[T](
	*args: Any, **kwargs: Any
) -> Callable[[Callable[..., T]], Callable[..., T]]:
	def decorator(tmp_comm: Callable[..., T]) -> Callable[..., T]:
		@main.parse_group.command(*args, **kwargs)
		@click.pass_context
		@functools.wraps(tmp_comm)
		def wrapper(ctx: click.Context, *args: Any, **kwargs: Any) -> T:
			return ctx.invoke(tmp_comm, ctx.obj["DATA"], *args, **kwargs)

		return wrapper

	return decorator
