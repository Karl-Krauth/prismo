class Valves:
    def __init__(self, name: str, valves=None):
        self.name = name
        if valves is None:
            valves = [i for i in range(48)]
        self.valves = {k: 1 for k in valves}

    def __getitem__(self, key):
        return self.valves[key]

    def __setitem__(self, key, value):
        self.valves[key] = int((value != "off") and (value != 0))


class Mux:
    def __init__(self, name, valves, mapping):
        self.name = name
        num_bits = (len(mapping) - 4) // 2
        self._zeros = [mapping[f"{i}_0"] for i in reversed(range(num_bits))]
        self._ones = [mapping[f"{i}_1"] for i in reversed(range(num_bits))]
        self._input = mapping["input"]
        self._all_inputs = self._zeros + self._ones + [self._input]
        self._purge = mapping["purge"]

        self._flow = mapping["flow"]
        self._waste = mapping["waste"]
        self._valves = valves

    @property
    def input(self):
        purge_state = 1 - self._valves[self._purge]
        input_state = 1 - self._valves[self._input]
        zeros_state = np.array([1 - self._valves[v] for v in self._zeros])
        ones_state = np.array([1 - self._valves[v] for v in self._ones])
        all_state = np.array([1 - self._valves[v] for v in self._all_inputs])
        if np.all(all_state) and not purge_state:
            return "open"
        elif not np.any(all_state) and not purge_state:
            return "closed"
        elif purge_state and not input_state:
            return "purge"
        elif np.all(zeros_state + ones_state == 1) and input_state and not purge_state:
            return sum(b * 2**i for i, b in enumerate(reversed(ones_state)))
        else:
            return "invalid"

    @input.setter
    def input(self, new_state):
        for v in self._all_inputs:
            self._valves[v] = 1
        self._valves[self._purge] = 1
        if new_state == "open":
            for v in self._all_inputs:
                self._valves[v] = 0
        elif new_state == "closed":
            pass
        elif new_state == "purge":
            for v in self._zeros:
                self._valves[v] = 0
            for v in self._ones:
                self._valves[v] = 0
            self._valves[self._purge] = 0
        elif isinstance(new_state, int):
            for i, b in enumerate(bin(new_state)[2:].zfill(len(self._ones))):
                if b == "0":
                    self._valves[self._zeros[i]] = 0
                else:
                    self._valves[self._ones[i]] = 0
            self._valves[self._input] = 0
        elif "purge" in new_state:
            new_state = int(new_state.split("_")[1])
            for i, b in enumerate(bin(new_state)[2:].zfill(len(self._ones))):
                if b == "0":
                    self._valves[self._zeros[i]] = 0
                else:
                    self._valves[self._ones[i]] = 0
            self._valves[self._purge] = 0

    @property
    def output(self):
        waste_state = 1 - self._valves[self._waste]
        flow_state = 1 - self._valves[self._flow]
        if waste_state and flow_state:
            return "open"
        elif waste_state:
            return "waste"
        elif flow_state:
            return "flow"
        else:
            return "closed"

    @output.setter
    def output(self, new_state):
        self._valves[self._waste] = 1
        self._valves[self._flow] = 1
        if new_state == "waste":
            self._valves[self._waste] = 0
        elif new_state == "flow":
            self._valves[self._flow] = 0
        elif new_state == "open":
            self._valves[self._flow] = 0
            self._valves[self._waste] = 0


class MiniChip:
    def __init__(self, name, valves, mapping):
        self.name = name
        num_bits = (len(mapping) - 2) // 2
        self._zeros = [mapping[f"{i}_0"] for i in reversed(range(num_bits))]
        self._ones = [mapping[f"{i}_1"] for i in reversed(range(num_bits))]
        self._all_io = self._zeros + self._ones
        self._buttons = mapping["buttons"]
        self._out = mapping["output"]
        self._sandwiches = mapping["sandwiches"]
        self._valves = valves

    @property
    def io(self):
        zeros_state = np.array([1 - self._valves[v] for v in self._zeros])
        ones_state = np.array([1 - self._valves[v] for v in self._ones])
        all_state = np.array([1 - self._valves[v] for v in self._all_io])
        if np.all(all_state):
            return "open"
        elif not np.any(all_state):
            return "closed"
        elif np.all(zeros_state + ones_state == 1):
            return sum(b * 2**i for i, b in enumerate(reversed(ones_state)))
        else:
            return "invalid"

    @io.setter
    def io(self, new_state):
        if new_state == "open":
            for v in self._all_io:
                self._valves[v] = 0
        elif new_state == "closed":
            for v in self._all_io:
                self._valves[v] = 1
        else:
            for v in self._all_io:
                self._valves[v] = 1

            for i, b in enumerate(bin(new_state)[2:].zfill(len(self._ones))):
                if b == "0":
                    self._valves[self._zeros[i]] = 0
                else:
                    self._valves[self._ones[i]] = 0

    @property
    def btn(self):
        return "closed" if self._valves[self._buttons] else "open"

    @btn.setter
    def btn(self, new_state):
        if new_state == "open" or not new_state:
            self._valves[self._buttons] = "off"
        else:
            self._valves[self._buttons] = "on"

    @property
    def output(self):
        return "closed" if self._valves[self._out] else "open"

    @output.setter
    def output(self, new_state):
        if new_state == "open" or not new_state:
            self._valves[self._out] = "off"
        else:
            self._valves[self._out] = "on"

    @property
    def snw(self):
        return "closed" if self._valves[self._sandwiches] else "open"

    @snw.setter
    def snw(self, new_state):
        if new_state == "open" or not new_state:
            self._valves[self._sandwiches] = "off"
        else:
            self._valves[self._sandwiches] = "on"
