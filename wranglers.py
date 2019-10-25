

from .missing import Missing

# just list of columns for the moment, no side effects?
# copy on creation, column storage
# returns value w[i,j]
# returns w[:,j] (returns column j), w[i,:]

class WranglerException(Exception):
    pass


class DataWrangler(object):

    @staticmethod
    def withCols(n):
        return ListWrangler([[] * n])

    @staticmethod
    def withColNames(names):
        raise NotImplementedError()

    def __init__(self, **kwargs):
        self._nd = kwargs.get('nd', Missing)
        if self._nd is Missing: raise WranglerException("kwarg 'nd' is required")
        assert self.nd == 2
        self._cols = []
        # if False:
        #     nRows = len(cols[0])
        #     for j, col in enumerate(cols):
        #         c = []
        #         if len(col) != nRows:
        #             raise WranglerException("len(row) != nCols")
        #         for i, value in enumerate(col):
        #             c.append(value)

    def __iadd__(self, other):
        # +=
        if self.nd > 1:
            raise WranglerException()
        raise NotImplementedError()

    def __imul__(self, other):
        # *=
        if self.nd > 1:
            raise WranglerException()
        raise NotImplementedError()

    def __isub__(self, other):
        # -=
        if self.nd > 1:
            raise WranglerException()
        raise NotImplementedError()

    def __itruediv__(self, other):
        # /=
        if self.nd > 1:
            raise WranglerException()
        raise NotImplementedError()

    def __ifloordiv__(self, other):
        # //=
        raise NotImplementedError()

    def __ipow__(self, other):
        # **=
        raise NotImplementedError()

    def __imod__(self, other):
        # %=
        raise NotImplementedError()


    @property
    def nd(self):
        return self._nd

    @property
    def d(selfself):
        raise NotImplementedError()

    # 2d convenience methods
    @property
    def d1(selfself):
        raise NotImplementedError()

    @property
    def d2(selfself):
        raise NotImplementedError()

    @property
    def rows(self):
        return _RowsView(self._cols, self)

    @rows.setter
    def rows(self, value):
        # do nothing as the list has already been changed by the _RowsView += method
        pass

    @property
    def cols(self):
        return _ColsView(self._cols, self)

    @cols.setter
    def cols(self, value):
        # do nothing as the list has already been changed by the _Colsiew += method
        pass

    @property
    def nCols(self):
        return len(self._cols)

    @property
    def nRows(self):
        return len(self._cols[0]) if len(self._cols) > 0 else 0



class _RowsView(object):
    def __init__(self, _cols, wrangler):
        self._cols = _cols
        self._wrangler = wrangler
    def __iadd__(self, row):
        if len(self._cols) == 0:
            # add the first row
            for val in row:
                self._cols.append([val])
        elif len(self._cols) != len(row):
            raise WranglerException()
        else:
            for i, val in enumerate(row):
                self._cols[i].append(val)
    @property
    def n(self):
        return self._wrangler.nRows

class _ColsView(object):
    def __init__(self, _cols, wrangler):
        self._cols = _cols
        self._wrangler = wrangler
    def __iadd__(self, col):
        if len(self._cols) == 0:
            # add the first col
            self._cols.append(list(col))
        elif len(self._cols) != len(col):
            raise WranglerException()
        else:
            self._cols.append(list(col))
    @property
    def n(self):
        return self._wrangler.nCols


