"""base62 인코딩: 0 이상의 정수 <-> 0-9, a-z, A-Z 문자열."""

DIGITS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = 62


def _digit_value(ch):
    if "0" <= ch <= "9":
        return ord(ch) - ord("0")
    if "a" <= ch <= "z":
        return ord(ch) - ord("a") + 10
    if "A" <= ch <= "Z":
        return ord(ch) - ord("A") + 36
    raise ValueError(f"base62에 없는 글자: {ch!r}")


def encode(n):
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("encode는 정수만 받습니다")
    if n < 0:
        raise ValueError("encode는 0 이상의 정수만 받습니다")
    if n == 0:
        return DIGITS[0]
    out = []
    while n > 0:
        n, r = divmod(n, BASE)
        out.append(DIGITS[r])
    return "".join(reversed(out))


def decode(s):
    if not isinstance(s, str):
        raise TypeError("decode는 문자열만 받습니다")
    if s == "":
        raise ValueError("빈 문자열은 decode할 수 없습니다")
    n = 0
    for ch in s:
        n = n * BASE + _digit_value(ch)
    return n
