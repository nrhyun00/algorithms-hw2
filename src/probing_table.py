"""선형 탐지(linear probing) 해시 테이블. HashTable과 같은 인터페이스.

칸 하나에 키 하나. 처음 칸 h = 호너 해시에서 시작해 h, h+1, h+2, ... (mod M)
순서로 빈 칸이나 같은 키를 찾는다. dict·set·내장 hash()를 쓰지 않는다.
"""

from hash_table import horner_hash

_EMPTY = None


class _Entry:
    __slots__ = ("key", "value")

    def __init__(self, key, value):
        self.key = key
        self.value = value


class LinearProbingTable:
    def __init__(self, capacity=16, max_load=0.5):
        if capacity < 1:
            raise ValueError("capacity는 1 이상이어야 합니다")
        self._m = capacity
        self._slots = [_EMPTY] * capacity
        self._n = 0
        self._max_load = max_load

    def __len__(self):
        return self._n

    def __contains__(self, key):
        return self.find(key)[0]

    def capacity(self):
        return self._m

    def load_factor(self):
        return self._n / self._m

    def index_of(self, key):
        return horner_hash(key, self._m)

    def _probe(self, key):
        """(칸 번호 또는 None, 들여다본 칸 수). 칸 번호는 같은 키가 있는 칸이나 첫 빈 칸."""
        i = self.index_of(key)
        looked = 0
        while looked < self._m:
            looked += 1
            entry = self._slots[i]
            if entry is _EMPTY or entry.key == key:
                return i, looked
            i = (i + 1) % self._m
        return None, looked

    def find(self, key):
        """(찾음, 값, 들여다본 칸 수). 빈 칸을 만나 멈춘 경우 그 빈 칸도 센다."""
        i, looked = self._probe(key)
        if i is None or self._slots[i] is _EMPTY:
            return False, None, looked
        return True, self._slots[i].value, looked

    def get(self, key):
        return self.find(key)[1]

    def put(self, key, value):
        i, _ = self._probe(key)
        if i is None:
            # 가득 찼고 같은 키도 없다: max_load와 상관없이 칸을 늘린 뒤 넣는다.
            self._resize(2 * self._m + 1)
            i, _ = self._probe(key)
        if self._slots[i] is not _EMPTY:
            self._slots[i].value = value
            return
        self._slots[i] = _Entry(key, value)
        self._n += 1
        if self._max_load is not None and self.load_factor() > self._max_load:
            self._resize(2 * self._m + 1)

    def items(self):
        for entry in self._slots:
            if entry is not _EMPTY:
                yield entry.key, entry.value

    def slots(self):
        """칸마다 None 또는 (키, 값, 처음 칸, 들여다본 칸 수). /table 화면용."""
        out = []
        for i, entry in enumerate(self._slots):
            if entry is _EMPTY:
                out.append(None)
            else:
                home = self.index_of(entry.key)
                out.append((entry.key, entry.value, home, (i - home) % self._m + 1))
        return out

    def _resize(self, new_m):
        old = list(self.items())
        self._m = new_m
        self._slots = [_EMPTY] * new_m
        self._n = 0
        for key, value in old:
            i, _ = self._probe(key)
            self._slots[i] = _Entry(key, value)
            self._n += 1
