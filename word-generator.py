import random
from typing import Iterator, Sequence, Set

# the most common letters in order of frequency as listed at
# https://pi.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
COMMON_LETTERS = "etaoinsrhdlucmfywgpbvkxqjz"
# COMMON_LETTERS = "asrhdlucmfywgpbvkxqjz"


def valid(word: str, common_letters: str, must: str) -> bool:
    if must not in word:
         return False
    for c in word:
        if c not in common_letters:
            return False
    return True


def main(length: int):
    words = tuple(gen_words("common-words.txt"))
    subset = COMMON_LETTERS[:length]

    print("only letters from: " + subset)
    for to_practice in gen_letters_to_practice(length):
        print(f"Practicing letter {to_practice}")
        candiates = tuple(w for w in words if valid(w, subset, to_practice))
        print(" ".join(random_subset(candiates, 20)))
        print()


def random_subset(data: tuple[str], count: int) -> tuple[str]:
    if len(data) < count:
        return data
    results: Set[str] = set()
    while len(results) < count - 1:
        candidate = random.choice(data)
        if candidate not in results:
            results.add(candidate)
    return tuple(results)


def gen_words(filename: str) -> Iterator[str]:
    with open(filename, "r") as f:
        for line in f:
            yield line.strip()


def gen_letters_to_practice(count: int) -> Iterator[str]:
    for i in range(4):
        yield COMMON_LETTERS[count - i - 1]


if __name__ == "__main__":
    main(15)
