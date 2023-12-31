from concurrent.futures import Future
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
    return f'{baseurl}/{urlpath}'


def profiles_with_dblp_url() -> str:
    return resolve_api_url('profiles')


def notes_url() -> str:
    return resolve_api_url('notes')


def _handle_response(response: Response) -> Response:
    try:
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as e:
        logger.error(f'HTTPError: {e} {e.args}')
        raise


T = TypeVar('T')


def list_to_optional(ts: List[T]) -> Optional[T]:
    match ts:
        case []:
            return None
        case [h]:
            return h
        case _:
            raise Exception(f'Expected 0 or 1 items, got {len(ts)}')


QueryParms = Any


def _note_fetcher(**params: QueryParms) -> List[Note]:
    with get_session() as s:
        future: Future[Response] = cast(Future[Response], s.get(notes_url(), params=params))
        rawresponse = future.result()
        response = _handle_response(rawresponse)
        notes = load_notes(response.json())
        return notes.notes


def _fetch_notes(*, slice: Optional[Slice], **initparams: QueryParms) -> Iterator[Note]:
    def _fetcher(**params: QueryParms) -> List[Note]:
        return _note_fetcher(**params)

    iter = IterGet(_fetcher, **initparams)

    if slice:
        iter = iter.withSlice(slice)

    return iter


def fetch_note(id: str) -> Optional[Note]:
    notes = _note_fetcher(id=id)
    return list_to_optional(notes)


def fetch_notes_for_dblp_rec_invitation(*, slice: Optional[Slice], newestFirst: bool = True) -> Iterator[Note]:
    sort = 'number:desc' if newestFirst else 'number:asc'
    return _fetch_notes(slice=slice, invitation='dblp.org/-/record', sort=sort)


def fetch_notes_for_author(authorid: str, invitation: Optional[str] = None) -> Iterator[Note]:
    if invitation:
        return _fetch_notes(slice=None, invitation=invitation, **{'content.authorids': authorid})
    return _fetch_notes(slice=None, **{'content.authorids': authorid})


def profile_fetcher(**params: QueryParms) -> List[Profile]:
    with get_session() as s:
        future: Future[Response] = cast(Future[Response], s.get(profiles_with_dblp_url(), params=params))
        rawresponse: Response = future.result()
        response = _handle_response(rawresponse)
        profiles = [load_profile(p) for p in response.json()['profiles']]
        return profiles


def fetch_profile(user_id: str) -> Optional[Profile]:
    if is_valid_email(user_id):
        return list_to_optional(profile_fetcher(emails=user_id))

    return list_to_optional(profile_fetcher(id=user_id))


def fetch_profile_with_dblp_pid(dblp_pid: str) -> Optional[Profile]:
    profiles = profile_fetcher(dblp=dblp_pid)
    return list_to_optional(profiles)
