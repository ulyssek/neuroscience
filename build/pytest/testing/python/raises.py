import pytest

class TestRaises:
    def test_raises(self):
        source = "int('qwe')"
        excinfo = pytest.raises(ValueError, source)
        code = excinfo.traceback[-1].frame.code
        s = str(code.fullsource)
        assert s == source

    def test_raises_exec(self):
        pytest.raises(ValueError, "a,x = []")

    def test_raises_syntax_error(self):
        pytest.raises(SyntaxError, "qwe qwe qwe")

    def test_raises_function(self):
        pytest.raises(ValueError, int, 'hello')

    def test_raises_callable_no_exception(self):
        class A:
            def __call__(self):
                pass
        try:
            pytest.raises(ValueError, A())
        except pytest.raises.Exception:
            pass

    def test_raises_flip_builtin_AssertionError(self):
        # we replace AssertionError on python level
        # however c code might still raise the builtin one
        from _pytest.assertion.util import BuiltinAssertionError
        pytest.raises(AssertionError,"""
            raise BuiltinAssertionError
        """)

    @pytest.mark.skipif('sys.version < "2.5"')
    def test_raises_as_contextmanager(self, testdir):
        testdir.makepyfile("""
            from __future__ import with_statement
            import py, pytest

            def test_simple():
                with pytest.raises(ZeroDivisionError) as excinfo:
                    assert isinstance(excinfo, py.code.ExceptionInfo)
                    1/0
                print (excinfo)
                assert excinfo.type == ZeroDivisionError

            def test_noraise():
                with pytest.raises(pytest.raises.Exception):
                    with pytest.raises(ValueError):
                           int()

            def test_raise_wrong_exception_passes_by():
                with pytest.raises(ZeroDivisionError):
                    with pytest.raises(ValueError):
                           1/0
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            '*3 passed*',
        ])

