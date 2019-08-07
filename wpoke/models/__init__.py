from datetime import datetime
from typing import AnyStr, Dict, List, Optional

import serpy


class TimeitResultMixin:
    started_at: datetime
    finished_at: datetime

    @property
    def runtime(self):
        return (self.finished_at - self.started_at).total_seconds()


class TimeitResultSerializerMixin:
    started_at = serpy.MethodField(required=True, method="get_started_at")
    finished_at = serpy.MethodField(required=True, method="get_finished_at")

    def _serialize_datetime(self, datetime_object):
        return datetime_object.isoformat()

    def get_started_at(self, model):
        return self._serialize_datetime(model.started_at)

    def get_finished_at(self, model):
        return self._serialize_datetime(model.finished_at)


class FingerResult(TimeitResultMixin):
    status: int
    finger_origin: AnyStr
    data: Dict
    errors: Optional[List[AnyStr]] = []


class FingerResultSerializer(serpy.Serializer, TimeitResultSerializerMixin):
    status = serpy.IntField(required=True)
    finger_origin = serpy.StrField(required=True)
    runtime = serpy.FloatField(required=True)
    data = serpy.Field(required=True)
    errors = serpy.Field(required=False)


class HandResult(TimeitResultMixin):
    loaded_fingers: List[str]
    serial_runtime: float
    parallel_runtime: float
    pokes: List[FingerResult]


class HandResultSerializer(serpy.Serializer, TimeitResultSerializerMixin):
    loaded_fingers = serpy.Field(required=True)
    serial_runtime = serpy.FloatField(required=True)
    parallel_runtime = serpy.FloatField(required=True)
    runtime = serpy.FloatField(required=True, label="real_runtime")
    pokes = FingerResultSerializer(required=True, many=True)
    started_at = serpy.MethodField(required=True, method="get_started_at")
    finished_at = serpy.MethodField(required=True, method="get_finished_at")
