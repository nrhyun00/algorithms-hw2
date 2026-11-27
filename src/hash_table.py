"""개별 체이닝 해시 테이블. dict·set·내장 hash()를 쓰지 않는다."""

R = 31


def horner_hash(key, m):
    h = 0
    for ch in key:
        h = (R * h + ord(ch)) % m
    return h


def horner_steps(key, m):
    """글자마다 (글자, ord, 이전 h, 새 h)를 돌려준다. /table 화면용."""
    steps = []
    h = 0
    for ch in key:
        new_h = (R * h + ord(ch)) % m
        steps.append((ch, ord(ch), h, new_h))
        h = new_h
    return steps


class _Node:
    __slots__ = ("key", "value", "next")

    def __init__(self, key, value, next_node):
        self.key = key
        self.value = value
        self.next = next_node


class HashTable:
    def __init__(self, capacity=16, max_load=1.0):
        if capacity < 1:
            raise ValueError("capacity는 1 이상이어야 합니다")
        self._m = capacity
        self._buckets = [None] * capacity
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

    def find(self, key):
        """(찾음, 값, 비교한 노드 수)."""
        compared = 0
        node = self._buckets[self.index_of(key)]
        while node is not None:
            compared += 1
            if node.key == key:
                return True, node.value, compared
            node = node.next
        return False, None, compared

    def get(self, key):
        return self.find(key)[1]

    def put(self, key, value):
        i = self.index_of(key)
        node = self._buckets[i]
        while node is not None:
            if node.key == key:
                node.value = value
                return
            node = node.next
        self._buckets[i] = _Node(key, value, self._buckets[i])
        self._n += 1
        if self._max_load is not None and self.load_factor() > self._max_load:
            self._resize(2 * self._m + 1)

    def items(self):
        for head in self._buckets:
            node = head
            while node is not None:
                yield node.key, node.value
                node = node.next

    def chains(self):
        """칸마다 [(키, 값), ...] 목록. /table 화면용."""
        out = []
        for head in self._buckets:
            chain = []
            node = head
            while node is not None:
                chain.append((node.key, node.value))
                node = node.next
            out.append(chain)
        return out

    def _resize(self, new_m):
        old = list(self.items())
        self._m = new_m
        self._buckets = [None] * new_m
        self._n = 0
        for key, value in old:
            i = self.index_of(key)
            self._buckets[i] = _Node(key, value, self._buckets[i])
            self._n += 1
