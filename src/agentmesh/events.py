"""In-process event bus with bounded subscriber queues and no external services."""
import asyncio
from dataclasses import dataclass
from datetime import datetime,timezone

@dataclass(frozen=True)
class AgentEvent:
    run_id:str
    agent:str
    status:str
    sequence:int
    timestamp:str

class EventBus:
    def __init__(self,max_queue=256):
        if not 1<=max_queue<=10000:raise ValueError("invalid queue")
        self.max_queue=max_queue
        self._subscribers=set()
    def subscribe(self):
        queue=asyncio.Queue(maxsize=self.max_queue)
        self._subscribers.add(queue)
        return queue
    def unsubscribe(self,queue):
        self._subscribers.discard(queue)
    def publish(self,event:AgentEvent):
        for queue in tuple(self._subscribers):
            if queue.full():queue.get_nowait()
            queue.put_nowait(event)
    @staticmethod
    def new_event(run_id,agent,status,sequence):
        return AgentEvent(run_id,agent,status,sequence,datetime.now(timezone.utc).isoformat())
