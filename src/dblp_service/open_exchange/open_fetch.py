from concurrent.futures import Future
import json
import pprint
from typing import Any, Iterator, TypeVar, cast
from typing import Optional, List, TypeAlias

import requests
from requests import Response

import openreview as op  # type: ignore

from requests_futures.sessions import FuturesSession  # type: ignore

from dblp_service.lib.log import create_logger
from ..lib.config import get_config
from ..lib.iterget import IterGet
from ..lib.typedefs import Slice
from ..lib.utils import is_valid_email


from .profile_schemas import Profile, load_profile
from .note_schemas import Note, load_notes
from os import path

logger = create_logger(__file__)

Session: TypeAlias = FuturesSession
cached_client: Optional[op.Client] = None


def get_client() -> op.Client:
    global cached_client
    if not cached_client:
        config = get_config()
        baseurl = config.openreview.restApi
        username = config.openreview.restUser
        password = config.openreview.restPassword
        cached_client = op.Client(baseurl=baseurl, username=username, password=password)

    assert cached_client is not None
    return cached_client


cached_session: Optional[Session] = None


def get_session() -> Session:
    client = get_client()
    session = FuturesSession()
    session.headers.update(client.headers)
    return session


def resolve_api_url(urlpath: str) -> str:
    config = get_config()
    baseurl = config.openreview.restApi
    return path.join(baseurl, urlpath)


def _handle_response(response: Response) -> Response:
    try:
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        logger.error(f'HTTPError: {e} {e.args}')
        raise


T = TypeVar('T')


def list_to_optional(ts: List[T]) -> Optional[T]:
    if not ts:
        return None
    if len(ts) > 1:
        raise Exception(f'Expected 0 or 1 items, got {len(ts)}')
    return ts[0]


QueryParms = Any


def _get_path(urlpath: str, **params: QueryParms) -> Response:
    url = resolve_api_url(urlpath)
    with get_session() as s:
        future: Future[Response] = cast(Future[Response], s.get(url, params=params))
        rawresponse = future.result()

        return _handle_response(rawresponse)


def _post_path(urlpath: str, payload: QueryParms) -> Response:
    url = resolve_api_url(urlpath)
    data = json.dumps(payload)
    with get_session() as s:
        future: Future[Response] = cast(Future[Response], s.post(url, data=data))
        rawresponse = future.result()

        pprint.pp(rawresponse)
        return _handle_response(rawresponse)


def _get_profile(**params: QueryParms) -> List[Profile]:
    response = _get_path('profiles', **params)
    profiles = [load_profile(p) for p in response.json()['profiles']]
    return profiles


def _get_notes(**params: QueryParms) -> List[Note]:
    response = _get_path('notes', **params)
    notes = load_notes(response.json())
    return notes.notes


def _get_note_search(**params: QueryParms) -> List[Note]:
    response = _get_path('notes/search', **params)
    notes = load_notes(response.json())
    return notes.notes


def _post_note_search(qparams: QueryParms) -> List[Note]:
    print(qparams)
    response = _post_path('notes/search', qparams)
    notes = load_notes(response.json())
    return notes.notes


def _get_note_iterator(*, slice: Optional[Slice], **initparams: QueryParms) -> Iterator[Note]:
    iter = IterGet(_get_notes, **initparams)

    if slice:
        iter = iter.withSlice(slice)

    return iter


def search_notes(*, title: str) -> List[Note]:
    return _get_note_search(
        **{'term': f'"{title}"', 'content': 'all', 'group': 'all', 'source': 'all'},
    )


def fetch_notes_for_author(authorid: str, invitation: Optional[str] = None) -> Iterator[Note]:
    if invitation:
        return _get_note_iterator(slice=None, invitation=invitation, **{'content.authorids': authorid})
    return _get_note_iterator(slice=None, **{'content.authorids': authorid})


def fetch_profile(user_id: str) -> Optional[Profile]:
    if is_valid_email(user_id):
        return list_to_optional(_get_profile(emails=user_id))

    return list_to_optional(_get_profile(id=user_id))


def fetch_profile_with_dblp_pid(dblp_pid: str) -> Optional[Profile]:
    profiles = _get_profile(dblp=dblp_pid)
    return list_to_optional(profiles)
