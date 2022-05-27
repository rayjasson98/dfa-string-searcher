class State():
    __slots__ = ['identifier', 'char', 'success', 'transitions',
                 'parent', 'matched_string', 'longest_proper_suffix']

    def __init__(self, identifier, char=None, parent=None, success=False):
        self.identifier = identifier
        self.char = char
        self.success = success
        self.transitions = {}
        self.parent = parent
        self.matched_string = None
        self.longest_proper_suffix = None

    def __str__(self):
        transitions_as_string = ','.join(
            [f'{key} -> {value.identifier}' for key, value in self.transitions.items()])

        return f'State {self.identifier}. Transitions: {transitions_as_string}'


class AhoCorasickAutomaton():
    def __init__(self, case_insensitive=False):
        self.initial_state = State(0)
        self.counter = 1
        self.finalized = False
        self.case_insensitive = case_insensitive

    def add(self, string):
        if len(string) <= 0:
            return

        original_string = string

        if self.case_insensitive:
            string = string.lower()

        current_state = self.initial_state

        for char in string:
            try:
                current_state = current_state.transitions[char]
            except KeyError:
                next_state = State(self.counter, parent=current_state,
                                   char=char)
                current_state.transitions[char] = next_state
                current_state = next_state

                self.counter += 1

        current_state.success = True
        current_state.matched_string = original_string

    def finalize(self):
        self.initial_state.longest_proper_suffix = self.initial_state
        self.search_lps_for_children(self.initial_state)
        self.finalized = True

    def search(self, text):
        if self.case_insensitive:
            text = text.lower()

        initial_state = self.initial_state
        current_state = initial_state

        for i, char in enumerate(text):
            default_state = initial_state.transitions.get(char, initial_state)
            current_state = current_state.transitions.get(char, default_state)

            state = current_state

            while state is not initial_state:
                if state.success:
                    string = state.matched_string

                    yield {
                        "value": string,
                        "start": i + 1 - len(string),
                        "end": i + 1
                    }

                state = state.longest_proper_suffix

    def search_lps_for_children(self, initial_state):
        processed_states = set()
        to_process_states = [initial_state]

        while to_process_states:
            state = to_process_states.pop()
            processed_states.add(state.identifier)

            for child in state.transitions.values():
                if child.identifier not in processed_states:
                    self.search_lps(child)
                    to_process_states.append(child)

    def search_lps(self, state):
        initial_state = self.initial_state
        parent = state.parent
        parent_lps = parent.longest_proper_suffix

        while True:
            if state.char in parent_lps.transitions and\
                    parent_lps.transitions[state.char] is not state:
                state.longest_proper_suffix = parent_lps.transitions[state.char]
                break

            if parent_lps is initial_state:
                state.longest_proper_suffix = initial_state
                break

            parent_lps = parent_lps.longest_proper_suffix

        state_lps = state.longest_proper_suffix

        if state_lps is initial_state:
            return

        if state_lps.longest_proper_suffix is None:
            self.search_lps(state_lps)

        for char, next_state in state_lps.transitions.items():
            if char not in state.transitions:
                state.transitions[char] = next_state
