# 구현 계획

SPEC.md를 기준으로 한다. 코드는 이 계획을 검토한 뒤에 쓴다.

## 순서

1. **테스트 먼저** (4단계)
   - `tests/test_hash_table.py`: SPEC 6절의 해시 테이블 경계 사례
   - `tests/test_shortener.py`: SPEC 6절의 단축기 경계 사례
   - 이 시점에 `make test` 가 실패하는 것은 정상
2. **`src/hash_table.py`**
   - `horner_hash(key, m)`: R = 31, `ord` 로 글자 값을 얻는다. 내장 `hash()` 를 쓰지 않는다.
   - `horner_steps(key, m)`: `/table` 화면용으로 글자마다 중간값을 돌려준다.
   - `_Node(key, value, next)` 연결 리스트, `HashTable` 은 칸 배열(`list`)만 가진다. `dict` 없음.
   - `find(key)` 는 `(찾음, 값, 비교한 노드 수)` 를 돌려준다. 실험에서 이 수를 센다.
   - 적재율이 `max_load` 를 넘으면 `2M + 1` 로 늘리고 다시 넣는다.
3. **`src/shortener.py`**
   - 테이블 두 개: URL → 코드, 코드 → URL.
   - 코드는 일련번호(1부터)를 `base62.encode`. URL의 해시값으로 만들지 않는다.
   - `validate(url)`: http/https, 공백, 호스트, 2048자.
4. **`make test` 통과 확인**, 테스트는 고치지 않는다.
5. **실험** (6단계): `experiments/probe_experiment.py`, M = 4093, `max_load=None`.
6. **서버** (7단계): `src/server.py`, `http.server` 만.

## 피해야 할 것

- `dict`·`set`·`hash()` 사용 → `grep` 으로 확인
- URL 해시값으로 코드 만들기 → 충돌 시 다른 URL이 같은 코드를 받음
- 테스트를 마지막에 쓰기
