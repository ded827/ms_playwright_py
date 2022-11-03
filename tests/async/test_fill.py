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

import pytest

from playwright.async_api import Error, Page
from tests.server import Server


async def test_fill_textarea(page, server):
    await page.goto(f"{server.PREFIX}/input/textarea.html")
    await page.fill("textarea", "some value")
    assert await page.evaluate("result") == "some value"


async def test_fill_input(page, server):
    await page.goto(f"{server.PREFIX}/input/textarea.html")
    await page.fill("input", "some value")
    assert await page.evaluate("result") == "some value"


async def test_should_throw_on_unsupported_inputs_when_clear(
    page: Page, server: Server
):
    await page.goto(f"{server.PREFIX}/input/textarea.html")
    for type in ["button", "checkbox", "file", "image", "radio", "reset", "submit"]:
        await page.eval_on_selector(
            "input", "(input, type) => input.setAttribute('type', type)", type
        )
        with pytest.raises(Error) as exc_info:
            await page.clear("input")
        assert f'Input of type "{type}" cannot be filled' in exc_info.value.message


async def test_it_should_throw_nice_error_without_injected_script_stack_when_element_is_not_an_input_when_clear(
    page: Page, server: Server
):
    await page.goto(server.PREFIX + "/input/textarea.html")
    with pytest.raises(Error) as exc_info:
        await page.clear("body")
    assert (
        "Element is not an <input>, <textarea> or [contenteditable] element"
        in exc_info.value.message
    )
