from typing import List, Dict, Optional

def add_numbers(a: int, b: int) -> int:
    return a + b

result = add_numbers("5", 10) 


class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def birthday(self) -> None:
        self.age += 1

user1 = User("Alice", "25") 

def get_scores(names: List[str]) -> List[Dict[str, int]]:
    scores = []
    for name in names:
        scores.append({"name": name, "score": str(100)})  
    return scores


def greet(user: Optional[User]) -> str:
    return "Hello " + user.name

greet(None)

def compute_average(scores: List[int]) -> float:
    total = sum(scores)
    return total / len(scores)

compute_average(["10", 20, 30]) 