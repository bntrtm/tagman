class Queue:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.insert(0, item)

    def pop(self):
        if len(self.items) == 0:
            return None
        item = self.items[len(self.items) - 1]
        del self.items[-1]
        return item

    def peek(self):
        if len(self.items) == 0:
            return None
        return self.items[-1]

    def size(self):
        return len(self.items)


class Trie:
    def __init__(self):
        self.root = {}
        self.end_symbol = "*"

    def longest_common_prefix(self):
        current = self.root
        prefix = ""
        while True:
            keys = list(current.keys())
            if self.end_symbol in keys:
                break
            if len(keys) == 1:
                prefix = prefix + keys[0]
                current = current[keys[0]]
            else:
                break
        return prefix

    def find_matches(self, document):
        matches = set()
        for i in range(len(document)):
            current = self.root
            for j in range(i, len(document)):
                if document[j] not in current:
                    break
                current = current[document[j]]
                if self.end_symbol in current:
                    matches.add(document[i : j + 1])
        return matches

    def search_level(self, current_level, current_prefix, words):
        if self.end_symbol in current_level:
            words.append(current_prefix)
        for key in sorted(current_level):
            if key != self.end_symbol:
                self.search_level(current_level[key], (current_prefix + key), words)
        return words

    def words_with_prefix(self, prefix):
        matching = []
        current = self.root
        for c in prefix:
            if c not in current:
                return []
            current = current[c]
        self.search_level(current, prefix, matching)
        return matching

    def exists(self, word):
        current = self.root
        for char in word:
            if char in current:
                current = current[char]
            else:
                return False
        if self.end_symbol in current:
            return True
        return False

    def get(self, word):
        """Returns a numeric value assigned to 'self.endsymbol'.

        A return value of 0 does NOT necessarily mean the word does not exist!
        """
        current = self.root
        for char in word:
            if char in current:
                current = current[char]
            else:
                return 0
        if self.end_symbol in current:
            if isinstance(current[self.end_symbol], int):
                return current[self.end_symbol]
        return 0

    def add(self, word):
        current = self.root
        for char in word:
            if char not in current:
                current[char] = {}
            current = current[char]
        if self.end_symbol not in current:
            current[self.end_symbol] = 1
        else:
            current[self.end_symbol] = current[self.end_symbol] + 1

    def remove(self, word):
        current = self.root
        parent_stack = []
        parent_keys = []
        for char in word:
            if char in current:
                parent_stack.append(current)
                parent_keys.append(char)
                current = current[char]
            else:
                # word does not exist in trie
                return
        if self.end_symbol in current:
            if current[self.end_symbol] > 1:
                current[self.end_symbol] = current[self.end_symbol] - 1
                return
            del current[self.end_symbol]
            while len(parent_stack) > 0:
                current = parent_stack.pop()
                key = parent_keys.pop()
                if len(current[key]) == 0:
                    del current[key]
                else:
                    break
        return

