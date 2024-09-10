import json
from typing import Final, Sequence, cast

from pydantic import TypeAdapter
from redis import Redis

from smartschedule.planning.project import Project
from smartschedule.planning.project_id import ProjectId
from smartschedule.planning.project_repository import ProjectRepository
from smartschedule.shared.repository import NotFound


class RedisProjectRepository(ProjectRepository):
    HASH_NAME: Final = "projects"

    def __init__(self, client: Redis) -> None:
        self._client = client
        self._type_adapter = TypeAdapter[Project](Project)

    def get(self, id: ProjectId) -> Project:
        if data := self._client.hget(self.HASH_NAME, self._id_to_key(id)):
            as_json = json.loads(cast(str, data))
            return self._type_adapter.validate_python(as_json)
        raise NotFound

    def get_all(self, ids: list[ProjectId] | None = None) -> Sequence[Project]:
        if ids is None:
            hash_contents = cast(dict[str, str], self._client.hgetall(self.HASH_NAME))
            raw_projects = list(hash_contents.values())
        else:
            keys = [self._id_to_key(id) for id in ids]
            raw_projects = cast(list[str], self._client.hmget(self.HASH_NAME, keys))
        return [
            self._type_adapter.validate_python(json.loads(data))
            for data in raw_projects
            if data
        ]

    def save(self, model: Project) -> None:
        key = self._id_to_key(model.id)
        as_dict = self._type_adapter.dump_python(model, mode="json")
        as_json = json.dumps(as_dict)
        self._client.hset(self.HASH_NAME, key, as_json)

    def _id_to_key(self, id: ProjectId) -> str:
        return id.id.hex
