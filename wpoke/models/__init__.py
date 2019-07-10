from datetime import datetime
from typing import AnyStr, Dict, List

import serpy


class FingerResult:
    status: int
    finger_origin: AnyStr
    started_at: datetime
    finished_at: datetime
    data: Dict

    @property
    def runtime(self):
        return (self.finished_at - self.started_at).total_seconds()


class FingerResultSerializer(serpy.Serializer):
    status = serpy.IntField(required=True)
    finger_origin = serpy.StrField(required=True)
    runtime = serpy.FloatField(required=True)
    started_at = serpy.MethodField(required=True, method='get_started_at')
    finished_at = serpy.MethodField(required=True, method='get_finished_at')
    data = serpy.Field(required=True)

    def _serialize_datetime(self, datetime_object):
        return datetime_object.isoformat()

    def get_started_at(self, model):
        return self._serialize_datetime(model.started_at)

    def get_finished_at(self, model):
        return self._serialize_datetime(model.finished_at)


class HandResult:
    loaded_fingers: List[str]
    serial_runtime: float
    parallel_runtime: float
    started_at: datetime
    finished_at: datetime
    pokes: List[FingerResult]

    @property
    def runtime(self):
        return (self.finished_at - self.started_at).total_seconds()


class HandResultSerializer(serpy.Serializer):
    loaded_fingers = serpy.Field(required=True)
    serial_runtime = serpy.FloatField(required=True)
    parallel_runtime = serpy.FloatField(required=True)
    runtime = serpy.FloatField(required=True, label='real_runtime')
    pokes = FingerResultSerializer(required=True, many=True)
    started_at = serpy.MethodField(required=True, method='get_started_at')
    finished_at = serpy.MethodField(required=True, method='get_finished_at')

    def _serialize_datetime(self, datetime_object):
        return datetime_object.isoformat()

    def get_started_at(self, model):
        return self._serialize_datetime(model.started_at)

    def get_finished_at(self, model):
        return self._serialize_datetime(model.finished_at)
