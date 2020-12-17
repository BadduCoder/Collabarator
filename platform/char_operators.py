def util_is_retain(var):
    return isinstance(var, int) and var > 0


def util_deletable(var):
    return isinstance(var, int) and var < 0


def util_insert(var):
    return isinstance(var, basestring)


def util_length(var):
    if isinstance(var, basestring):
        return len(var)
    if var < 0:
        return -var
    return var


def util_shorten(var, factor):
    if isinstance(var, basestring):
        return var[factor:]
    if var < 0:
        return var + factor
    return var - factor


def util_shorten_related(x, y):
    if util_length(x) == util_length(y):
        return (None, None)
    if util_length(x) > util_length(y):
        return (util_shorten(x, util_length(y)), None)
    return (None, util_shorten(y, util_length(x)))


class StringProps(object):
    """Diff between two strings."""

    def __init__(self, var=[]):
        self.var = var[:]

    def __iter__(self):
        return self.var.__iter__()

    def __add__(self, other):
        return self.complex_mix(other)

    def __eq__(self, other):
        return isinstance(other, StringProps) and self.var == other.var

    def diff_len(self):
        loop_count = 0
        for var in self:
            if isinstance(var, basestring):
                loop_count += len(var)
            elif var < 0:
                loop_count += var
        return loop_count

    def char_retain(self, x):
        if x == 0:
            return self
        if len(self.var) > 0 \
                and \
                isinstance(self.var[-1], int) \
                and \
                self.var[-1] > 0:

            self.var[-1] += x
        else:
            self.var.append(x)
        return self

    def char_insert(self, data):

        if len(data) == 0:
            return self
        if len(self.var) > 0 and isinstance(self.var[-1], basestring):
            self.var[-1] += data
        elif len(self.var) > 0 \
                and \
                isinstance(self.var[-1], int) \
                and \
                self.var[-1] < 0:
            if len(self.var) > 1 \
                    and \
                    isinstance(self.var[-2], basestring):
                self.var[-2] += data
            else:
                self.var.append(self.var[-1])
                self.var[-2] = data
        else:
            self.var.append(data)
        return self

    def chars_delete(self, data):

        if data == 0:
            return self
        if data > 0:
            data = -data
        if len(self.var) > 0 \
                and \
                isinstance(self.var[-1], int) \
                and \
                self.var[-1] < 0:
            self.var[-1] += data
        else:
            self.var.append(data)
        return self

    def __call__(self, doc):

        loop_counter = 0
        partial = []

        for op in self:
            if util_is_retain(op):
                if loop_counter + op > len(doc):
                    raise Exception("Exception occurred! Operation too long.")
                partial.append(doc[loop_counter:(loop_counter + op)])
                loop_counter += op
            elif util_insert(op):
                partial.append(op)
            else:
                loop_counter -= op
                if loop_counter > len(doc):
                    raise IncompatibleError("Exception occurred! Operation too long.")

        if loop_counter != len(doc):
            raise IncompatibleError("Exception occurred! Operation too short.")

        return ''.join(partial)

    def invert_undo(self, doc):

        i = 0
        inverse = StringProps()

        for op in self:
            if util_is_retain(op):
                inverse.char_retain(op)
                i += op
            elif util_insert(op):
                inverse.chars_delete(len(op))
            else:
                inverse.char_insert(doc[i:(i - op)])
                i -= op

        return inverse

    def complex_mix(self, other):

        iter_a = iter(self)
        iter_b = iter(other)
        operation = StringProps()

        a = b = None
        while True:
            if a == None:
                a = next(iter_a, None)
            if b == None:
                b = next(iter_b, None)

            if a == b == None:
                break

            if util_deletable(a):
                operation.chars_delete(a)
                a = None
                continue
            if util_insert(b):
                operation.char_insert(b)
                b = None
                continue

            if a == None:
                raise IncompatibleError("Exception occurred! first operation too long.")
            if b == None:
                raise IncompatibleError("Exception occurred! first operation too long.")

            min_len = min(util_length(a), util_length(b))
            if util_is_retain(a) and util_is_retain(b):
                operation.char_retain(min_len)
            elif util_insert(a) and util_is_retain(b):
                operation.char_insert(a[:min_len])
            elif util_is_retain(a) and util_deletable(b):
                operation.chars_delete(min_len)

            (a, b) = util_shorten_related(a, b)

        return operation

    @staticmethod
    def char_trans(operation_a, operation_b):

        iter_a = iter(operation_a)
        iter_b = iter(operation_b)
        a_prime = StringProps()
        b_prime = StringProps()
        a = b = None

        while True:
            if a == None:
                a = next(iter_a, None)
            if b == None:
                b = next(iter_b, None)

            if a == b == None:
                break

            if util_insert(a):
                a_prime.char_insert(a)
                b_prime.char_retain(len(a))
                a = None
                continue
            if util_insert(b):
                a_prime.char_retain(len(b))
                b_prime.char_insert(b)
                b = None
                continue

            if a == None:
                raise IncompatibleError("Exception occurred! first operation too short.")
            if b == None:
                raise IncompatibleError("Exception occurred! first operation too long.")

            min_len = min(util_length(a), util_length(b))
            if util_is_retain(a) and util_is_retain(b):
                a_prime.char_retain(min_len)
                b_prime.char_retain(min_len)
            elif util_deletable(a) and util_is_retain(b):
                a_prime.chars_delete(min_len)
            elif util_is_retain(a) and util_deletable(b):
                b_prime.chars_delete(min_len)

            (a, b) = util_shorten_related(a, b)

        return (a_prime, b_prime)


class IncompatibleError(Exception):
    pass
