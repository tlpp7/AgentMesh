"""Optional extension registry; never loads modules or executes code implicitly."""
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Extension:
    name: str
    category: str
    factory: Callable
    def __post_init__(self):
        if not self.name or self.category not in {"api","agents","events","storage","metrics","tools","compute"}:
            raise ValueError("invalid extension")

class ExtensionRegistry:
    def __init__(self):self._items={}
    def register(self, extension: Extension):
        key=(extension.category,extension.name)
        if key in self._items:raise ValueError("duplicate extension")
        self._items[key]=extension
    def list(self, category=None):
        return sorted({"name":e.name,"category":e.category} for e in self._items.values()
                      if category is None or e.category==category,key=lambda x:(x["category"],x["name"]))
    def create(self,category,name,**kwargs):
        return self._items[(category,name)].factory(**kwargs)
