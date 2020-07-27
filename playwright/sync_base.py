# Copyright (c) Microsoft Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
from typing import Any, Callable, Generic, Optional, TypeVar, cast

from playwright.impl_to_api_mapping import ImplToApiMapping, ImplWrapper
from playwright.wait_helper import WaitHelper

mapping = ImplToApiMapping()


T = TypeVar("T")


class EventInfo(Generic[T]):
    def __init__(
        self,
        sync_base: "SyncBase",
        event: str,
        predicate: Callable[[T], bool] = None,
        timeout: int = None,
    ) -> None:
        self._value: Optional[T] = None

        wait_helper = WaitHelper()
        wait_helper.reject_on_timeout(
            timeout or 30000, f'Timeout while waiting for event "${event}"'
        )
        self._future = asyncio.get_event_loop().create_task(
            wait_helper.wait_for_event(sync_base._impl_obj, event, predicate)
        )

    @property
    def value(self) -> T:
        if not self._value:
            value = asyncio.get_event_loop().run_until_complete(self._future)
            self._value = mapping.from_maybe_impl(value)
        return cast(T, self._value)


class EventContextManager(Generic[T]):
    def __init__(
        self,
        sync_base: "SyncBase",
        event: str,
        predicate: Callable[[T], bool] = None,
        timeout: int = None,
    ) -> None:
        self._event = EventInfo(sync_base, event, predicate, timeout)

    def __enter__(self) -> EventInfo[T]:
        return self._event

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self._event.value


class SyncBase(ImplWrapper):
    def __init__(self, impl_obj: Any) -> None:
        super().__init__(impl_obj)

    def __str__(self) -> str:
        return self._impl_obj.__str__()

    def _sync(self, future: asyncio.Future) -> Any:
        return asyncio.get_event_loop().run_until_complete(future)

    def _wrap_handler(self, handler: Any) -> Callable[..., None]:
        if callable(handler):
            return mapping.wrap_handler(handler)
        return handler

    def on(self, event_name: str, handler: Any) -> None:
        self._impl_obj.on(event_name, self._wrap_handler(handler))

    def once(self, event_name: str, handler: Any) -> None:
        self._impl_obj.once(event_name, self._wrap_handler(handler))

    def remove_listener(self, event_name: str, handler: Any) -> None:
        self._impl_obj.remove_listener(event_name, handler)

    def expect_event(
        self, event: str, predicate: Callable[[Any], bool] = None, timeout: int = None,
    ) -> EventContextManager:
        return EventContextManager(self, event, predicate, timeout)
