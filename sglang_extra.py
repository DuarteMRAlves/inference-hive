from __future__ import annotations

import httpx

from openai import OpenAI as OpenAIBase, AsyncOpenAI as AsyncOpenAIBase
from openai._base_client import make_request_options, DEFAULT_MAX_RETRIES
from openai._compat import cached_property
from openai._models import BaseModel
from openai._resource import SyncAPIResource, AsyncAPIResource
from openai._types import NOT_GIVEN, Body, Query, Headers, NotGiven, Timeout
from openai._utils import maybe_transform
from openai._response import to_streamed_response_wrapper
from openai._streaming import Stream

from typing import Iterable, List, Mapping, Union
from typing_extensions import Literal, Required, TypedDict


class OpenAI(OpenAIBase):
    classifications: Classifications

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        super().__init__(
            api_key=api_key,
            organization=organization,
            project=project,
            base_url=base_url,
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )

        self.classifications = Classifications(self)



class Classifications(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClassificationsWithRawResponse:
        return ClassificationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClassificationsWithStreamingResponse:
        return ClassificationsWithStreamingResponse(self)

    def create(
        self,
        *,
        text: Union[str, List[str], Iterable[int], Iterable[Iterable[int]]],
        model: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Classification:
        return self._post(
            "/classify",
            body=maybe_transform(
                {
                    "model": model,
                    "text": text,
                },
                ClassificationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=Classification,
        )


class ClassificationsWithRawResponse:
    def __init__(self, classifications: Classifications) -> None:
        self._classifications = classifications

        self.create = _legacy_response.to_raw_response_wrapper(
            classifications.create,
        )


class ClassificationsWithStreamingResponse:
    def __init__(self, classifications: Classifications) -> None:
        self._classifications = classifications

        self.create = to_streamed_response_wrapper(
            classifications.create,
        )


class AsyncOpenAI(AsyncOpenAIBase):
    classifications: AsyncClassifications

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        super().__init__(
            api_key=api_key,
            organization=organization,
            project=project,
            base_url=base_url,
            websocket_base_url=websocket_base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )

        self.classifications = AsyncClassifications(self)


class AsyncClassifications(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClassificationsWithRawResponse:
        return AsyncClassificationsWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClassificationsWithStreamingResponse:
        return AsyncClassificationsWithStreamingResponse(self)

    async def create(
        self,
        *,
        text: Union[str, List[str], Iterable[int], Iterable[Iterable[int]]],
        model: str,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Classification:
        return await self._post(
            "/classify",
            body=maybe_transform(
                {
                    "model": model,
                    "text": text,
                },
                ClassificationCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=Classification,
        )


class AsyncClassificationsWithRawResponse:
    def __init__(self, classifications: AsyncClassifications) -> None:
        self._classifications = classifications

        self.create = _legacy_response.to_raw_response_wrapper(
            classifications.create,
        )


class AsyncClassificationsWithStreamingResponse:
    def __init__(self, classifications: AsyncClassifications) -> None:
        self._classifications = classifications

        self.create = to_streamed_response_wrapper(
            classifications.create,
        )


class ClassificationCreateParams(TypedDict, total=False):
    text: Required[Union[str, List[str], Iterable[int], Iterable[Iterable[int]]]]
    model: Required[str]


class Classification(BaseModel):
    embedding: list[float]
    meta_info: ClassificationMetaInfo


class ClassificationMetaInfo(BaseModel):
    id: str
    finish_reason: ClassificationFinishReason
    prompt_tokens: int
    e2e_latency: float
    

class ClassificationFinishReason(BaseModel):
    type: Literal["length"]
    length: int = 0