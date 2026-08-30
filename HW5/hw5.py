import numpy as np

T, F = True, False

def extend(s, var, val):

    d = dict(s)
    d[var] = val
    return d

class ProbDist:
    def __init__(self, var_name='?', freq=None):
        self.prob = {}
        self.var_name = var_name
        self.values = []
        if freq:
            for (v, p) in freq.items():
                self[v] = p
            self.normalize()

    def __getitem__(self, val):
        return self.prob.get(val, 0)

    def __setitem__(self, val, p):
        if val not in self.values:
            self.values.append(val)
        self.prob[val] = p

    def normalize(self):
        total = sum(self.prob.values())
        if not np.isclose(total, 1.0) and total > 0:
            for val in self.prob:
                self.prob[val] /= total
        return self

def event_values(event, variables):
    if isinstance(event, tuple) and len(event) == len(variables):
        return event
    return tuple([event[var] for var in variables])

class BayesNode:
    def __init__(self, X, parents, cpt):
        if isinstance(parents, str):
            parents = parents.split()
        if isinstance(cpt, (float, int)):
            cpt = {(): cpt}
        elif isinstance(cpt, dict):
            if cpt and isinstance(list(cpt.keys())[0], bool):
                cpt = {(v,): p for v, p in cpt.items()}
        self.variable = X
        self.parents = parents
        self.cpt = cpt
        self.children = []

    def p(self, value, event):
        ptrue = self.cpt[event_values(event, self.parents)]
        return ptrue if value else 1 - ptrue

class BayesNet:
    def __init__(self, node_specs=None):
        self.nodes = []
        self.variables = []
        for node_spec in (node_specs or []):
            self.add(node_spec)

    def add(self, node_spec):
        node = BayesNode(*node_spec)
        self.nodes.append(node)
        self.variables.append(node.variable)
        for parent in node.parents:
            self.variable_node(parent).children.append(node)

    def variable_node(self, var):
        for n in self.nodes:
            if n.variable == var:
                return n
        raise Exception(f"No such variable: {var}")

    def variable_values(self, var):
        return [True, False]

def enumerate_all(variables, e, bn):
    if not variables:
        return 1.0
    Y, rest = variables[0], variables[1:]
    Ynode = bn.variable_node(Y)
    if Y in e:
        return Ynode.p(e[Y], e) * enumerate_all(rest, e, bn)
    else:
        return sum(Ynode.p(y, e) * enumerate_all(rest, extend(e, Y, y), bn)
                   for y in bn.variable_values(Y))

def enumeration_ask(X, e, bn):
    Q = ProbDist(X)
    for xi in bn.variable_values(X):
        Q[xi] = enumerate_all(bn.variables, extend(e, X, xi), bn)
    return Q.normalize()


medical_net = BayesNet([
    ('Smoker', '', 0.30),
    ('Cancer', 'Smoker', {T: 0.05, F: 0.01}),
    ('XRay', 'Cancer', {T: 0.90, F: 0.20})
])


print("ข้อ 1  ตอบ:", enumerate_all(medical_net.variables, {'Smoker': T, 'Cancer': T, 'XRay': T}, medical_net))
print("ข้อ 2  ตอบ:", enumeration_ask('XRay', {}, medical_net)[T])
print("ข้อ 3  ตอบ:", round(enumeration_ask('Cancer', {'XRay': T}, medical_net)[T], 3))
print("ข้อ 4  คอบ:", round(enumeration_ask('Smoker', {'XRay': T}, medical_net)[T], 3))

prob_C_and_X = enumerate_all(medical_net.variables, {'Cancer': T, 'XRay': T}, medical_net)
print("ข้อ 5  ตอบ:", round(1000 * prob_C_and_X, 1), )