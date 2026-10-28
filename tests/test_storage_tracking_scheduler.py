"""Tests for the Pironman storage tracking scheduler."""

import ast
import asyncio
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "custom_components/pironman5/sensor.py"
)


def make_scheduler(coordinator):
    """Load the actual nested scheduler functions in an isolated scope."""
    tree = ast.parse(SOURCE.read_text())

    setup = next(
        node for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "async_setup_entry"
    )

    names = {
        "track_storage",
        "schedule_storage_tracking",
        "stop_storage_tracking",
    }

    functions = [
        node for node in setup.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in names
    ]

    if len(functions) != 3:
        raise AssertionError("Scheduler functions not found")

    async def factory():
        tracking_task = None
        tracking_stopped = False
        tracking_pending = False
        reported_due_devices = set()

        logger = logging.getLogger("pironman5.test")

        hass = SimpleNamespace(
            async_create_task=asyncio.create_task
        )

        namespace = {
            "asyncio": asyncio,
            "logger": logger,
            "coordinator": coordinator,
            "hass": hass,
        }

        # Nested functions require a shared enclosing scope.
        wrapper = ast.AsyncFunctionDef(
            name="build",
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[
                ast.Assign(
                    targets=[ast.Name(id=name, ctx=ast.Store())],
                    value=ast.Constant(value=None if name == "tracking_task" else False),
                )
                for name in (
                    "tracking_task",
                    "tracking_stopped",
                    "tracking_pending",
                )
            ]
            + [
                ast.Assign(
                    targets=[
                        ast.Name(
                            id="reported_due_devices",
                            ctx=ast.Store(),
                        )
                    ],
                    value=ast.Call(
                        func=ast.Name(id="set", ctx=ast.Load()),
                        args=[],
                        keywords=[],
                    ),
                )
            ]
            + functions
            + [
                ast.Return(
                    value=ast.Tuple(
                        elts=[
                            ast.Name(id=name, ctx=ast.Load())
                            for name in (
                                "schedule_storage_tracking",
                                "stop_storage_tracking",
                            )
                        ],
                        ctx=ast.Load(),
                    )
                )
            ],
            decorator_list=[],
            returns=None,
            type_comment=None,
        )

        module = ast.fix_missing_locations(
            ast.Module(body=[wrapper], type_ignores=[])
        )

        exec(compile(module, str(SOURCE), "exec"), namespace)
        return await namespace["build"]()

    return factory()


@pytest.mark.asyncio
async def test_refresh_during_tracking_is_processed():
    started = asyncio.Event()
    release = asyncio.Event()
    calls = 0

    class Coordinator:
        last_update_success = True

        async def async_track_storage_absence(self):
            nonlocal calls
            calls += 1
            if calls == 1:
                started.set()
                await release.wait()
            return set()

    schedule, stop = await make_scheduler(Coordinator())

    schedule()
    await asyncio.wait_for(started.wait(), 1)

    schedule()
    release.set()

    await asyncio.sleep(0.05)

    assert calls == 2
    stop()


@pytest.mark.asyncio
async def test_multiple_refreshes_are_coalesced():
    started = asyncio.Event()
    release = asyncio.Event()
    calls = 0

    class Coordinator:
        last_update_success = True

        async def async_track_storage_absence(self):
            nonlocal calls
            calls += 1
            if calls == 1:
                started.set()
                await release.wait()
            return set()

    schedule, stop = await make_scheduler(Coordinator())

    schedule()
    await asyncio.wait_for(started.wait(), 1)

    for _ in range(10):
        schedule()

    release.set()
    await asyncio.sleep(0.05)

    assert calls == 2
    stop()


@pytest.mark.asyncio
async def test_unload_cancels_pending_work():
    started = asyncio.Event()
    cancelled = asyncio.Event()
    calls = 0

    class Coordinator:
        last_update_success = True

        async def async_track_storage_absence(self):
            nonlocal calls
            calls += 1
            started.set()

            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelled.set()
                raise

    schedule, stop = await make_scheduler(Coordinator())

    schedule()
    await asyncio.wait_for(started.wait(), 1)

    schedule()
    stop()

    await asyncio.wait_for(cancelled.wait(), 1)
    await asyncio.sleep(0)

    assert calls == 1
