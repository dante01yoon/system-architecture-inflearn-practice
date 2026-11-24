"""과반 투표로 리더 뽑기(Raft의 선거를 아주 줄인 모양): 임기마다 한 표, 전체의 과반을 얻어야 리더."""


class Node:
    def __init__(self, name):
        self.name, self.voted = name, {}         # 임기 → 표를 준 후보

    def vote(self, term, candidate):
        if term in self.voted:
            return self.voted[term] == candidate  # 한 임기에 한 표만
        self.voted[term] = candidate
        return True


def elect(candidate, term, reachable, total):
    """candidate가 닿는 노드들(reachable, 자기 포함)에게 표를 구한다. 과반이면 리더."""
    votes = [n.name for n in reachable if n.vote(term, candidate.name)]
    return votes, len(votes) > total // 2
