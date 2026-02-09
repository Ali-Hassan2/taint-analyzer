from typing import List, Dict, Optional

# Function with intentional type error
def add_numbers(a: int, b: int) -> int:
    return a + b

# This will cause a type error
result = add_numbers("5", 10)  # ❌ a should be int, given str

# Class with method type issues
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def birthday(self) -> None:
        self.age += 1

# Intentional error: passing wrong type
user1 = User("Alice", "25")  # ❌ age should be int

# Function returning list of dicts but wrong types inside
def get_scores(names: List[str]) -> List[Dict[str, int]]:
    scores = []
    for name in names:
        scores.append({"name": name, "score": str(100)})  # ❌ score should be int
    return scores

# Optional / None type mismatch
def greet(user: Optional[User]) -> str:
    return "Hello " + user.name  # ❌ if None passed, attribute error

greet(None)

# Complex function with multiple type errors
def compute_average(scores: List[int]) -> float:
    total = sum(scores)
    return total / len(scores)

compute_average(["10", 20, 30])  # ❌ str in list instead of int