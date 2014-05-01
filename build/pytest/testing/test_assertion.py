import sys

import py, pytest
import _pytest.assertion as plugin
from _pytest.assertion import reinterpret, util

needsnewassert = pytest.mark.skipif("sys.version_info < (2,6)")


@pytest.fixture
def mock_config():
    class Config(object):
        verbose = False
        def getoption(self, name):
            if name == 'verbose':
                return self.verbose
            raise KeyError('Not mocked out: %s' % name)
    return Config()


def interpret(expr):
    return reinterpret.reinterpret(expr, py.code.Frame(sys._getframe(1)))

class TestBinReprIntegration:
    pytestmark = needsnewassert

    def test_pytest_assertrepr_compare_called(self, testdir):
        testdir.makeconftest("""
            l = []
            def pytest_assertrepr_compare(op, left, right):
                l.append((op, left, right))
            def pytest_funcarg__l(request):
                return l
        """)
        testdir.makepyfile("""
            def test_hello():
                assert 0 == 1
            def test_check(l):
                assert l == [("==", 0, 1)]
        """)
        result = testdir.runpytest("-v")
        result.stdout.fnmatch_lines([
            "*test_hello*FAIL*",
            "*test_check*PASS*",
        ])

def callequal(left, right, verbose=False):
    config = mock_config()
    config.verbose = verbose
    return plugin.pytest_assertrepr_compare(config, '==', left, right)


class TestAssert_reprcompare:
    def test_different_types(self):
        assert callequal([0, 1], 'foo') is None

    def test_summary(self):
        summary = callequal([0, 1], [0, 2])[0]
        assert len(summary) < 65

    def test_text_diff(self):
        diff = callequal('spam', 'eggs')[1:]
        assert '- spam' in diff
        assert '+ eggs' in diff

    def test_text_skipping(self):
        lines = callequal('a'*50 + 'spam', 'a'*50 + 'eggs')
        assert 'Skipping' in lines[1]
        for line in lines:
            assert 'a'*50 not in line

    def test_text_skipping_verbose(self):
        lines = callequal('a'*50 + 'spam', 'a'*50 + 'eggs', verbose=True)
        assert '- ' + 'a'*50 + 'spam' in lines
        assert '+ ' + 'a'*50 + 'eggs' in lines

    def test_multiline_text_diff(self):
        left = 'foo\nspam\nbar'
        right = 'foo\neggs\nbar'
        diff = callequal(left, right)
        assert '- spam' in diff
        assert '+ eggs' in diff

    def test_list(self):
        expl = callequal([0, 1], [0, 2])
        assert len(expl) > 1

    def test_list_different_lenghts(self):
        expl = callequal([0, 1], [0, 1, 2])
        assert len(expl) > 1
        expl = callequal([0, 1, 2], [0, 1])
        assert len(expl) > 1

    def test_dict(self):
        expl = callequal({'a': 0}, {'a': 1})
        assert len(expl) > 1

    def test_set(self):
        expl = callequal(set([0, 1]), set([0, 2]))
        assert len(expl) > 1

    def test_frozenzet(self):
        expl = callequal(frozenset([0, 1]), set([0, 2]))
        print (expl)
        assert len(expl) > 1

    def test_list_tuples(self):
        expl = callequal([], [(1,2)])
        assert len(expl) > 1
        expl = callequal([(1,2)], [])
        assert len(expl) > 1

    def test_list_bad_repr(self):
        class A:
            def __repr__(self):
                raise ValueError(42)
        expl = callequal([], [A()])
        assert 'ValueError' in "".join(expl)
        expl = callequal({}, {'1': A()})
        assert 'faulty' in "".join(expl)

    def test_one_repr_empty(self):
        """
        the faulty empty string repr did trigger
        a unbound local error in _diff_text
        """
        class A(str):
            def __repr__(self):
                return ''
        expl = callequal(A(), '')
        assert not expl

    def test_repr_no_exc(self):
        expl = ' '.join(callequal('foo', 'bar'))
        assert 'raised in repr()' not in expl

def test_python25_compile_issue257(testdir):
    testdir.makepyfile("""
        def test_rewritten():
            assert 1 == 2
        # some comment
    """)
    result = testdir.runpytest()
    assert result.ret == 1
    result.stdout.fnmatch_lines("""
            *E*assert 1 == 2*
            *1 failed*
    """)

@needsnewassert
def test_rewritten(testdir):
    testdir.makepyfile("""
        def test_rewritten():
            assert "@py_builtins" in globals()
    """)
    assert testdir.runpytest().ret == 0

def test_reprcompare_notin(mock_config):
    detail = plugin.pytest_assertrepr_compare(
        mock_config, 'not in', 'foo', 'aaafoobbb')[1:]
    assert detail == ["'foo' is contained here:", '  aaafoobbb', '?    +++']

@needsnewassert
def test_pytest_assertrepr_compare_integration(testdir):
    testdir.makepyfile("""
        def test_hello():
            x = set(range(100))
            y = x.copy()
            y.remove(50)
            assert x == y
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*def test_hello():*",
        "*assert x == y*",
        "*E*Extra items*left*",
        "*E*50*",
    ])

@needsnewassert
def test_sequence_comparison_uses_repr(testdir):
    testdir.makepyfile("""
        def test_hello():
            x = set("hello x")
            y = set("hello y")
            assert x == y
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*def test_hello():*",
        "*assert x == y*",
        "*E*Extra items*left*",
        "*E*'x'*",
        "*E*Extra items*right*",
        "*E*'y'*",
    ])


@pytest.mark.xfail("sys.version_info < (2,6)")
def test_assert_compare_truncate_longmessage(testdir):
    testdir.makepyfile(r"""
        def test_long():
            a = list(range(200))
            b = a[::2]
            a = '\n'.join(map(str, a))
            b = '\n'.join(map(str, b))
            assert a == b
    """)

    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*truncated*use*-vv*",
    ])


    result = testdir.runpytest('-vv')
    result.stdout.fnmatch_lines([
        "*- 197",
    ])


@needsnewassert
def test_assertrepr_loaded_per_dir(testdir):
    testdir.makepyfile(test_base=['def test_base(): assert 1 == 2'])
    a = testdir.mkdir('a')
    a_test = a.join('test_a.py')
    a_test.write('def test_a(): assert 1 == 2')
    a_conftest = a.join('conftest.py')
    a_conftest.write('def pytest_assertrepr_compare(): return ["summary a"]')
    b = testdir.mkdir('b')
    b_test = b.join('test_b.py')
    b_test.write('def test_b(): assert 1 == 2')
    b_conftest = b.join('conftest.py')
    b_conftest.write('def pytest_assertrepr_compare(): return ["summary b"]')
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
            '*def test_base():*',
            '*E*assert 1 == 2*',
            '*def test_a():*',
            '*E*assert summary a*',
            '*def test_b():*',
            '*E*assert summary b*'])


def test_assertion_options(testdir):
    testdir.makepyfile("""
        def test_hello():
            x = 3
            assert x == 4
    """)
    result = testdir.runpytest()
    assert "3 == 4" in result.stdout.str()
    off_options = (("--no-assert",),
                   ("--nomagic",),
                   ("--no-assert", "--nomagic"),
                   ("--assert=plain",),
                   ("--assert=plain", "--no-assert"),
                   ("--assert=plain", "--nomagic"),
                   ("--assert=plain", "--no-assert", "--nomagic"))
    for opt in off_options:
        result = testdir.runpytest(*opt)
        assert "3 == 4" not in result.stdout.str()

def test_old_assert_mode(testdir):
    testdir.makepyfile("""
        def test_in_old_mode():
            assert "@py_builtins" not in globals()
    """)
    result = testdir.runpytest("--assert=reinterp")
    assert result.ret == 0

def test_triple_quoted_string_issue113(testdir):
    testdir.makepyfile("""
        def test_hello():
            assert "" == '''
    '''""")
    result = testdir.runpytest("--fulltrace")
    result.stdout.fnmatch_lines([
        "*1 failed*",
    ])
    assert 'SyntaxError' not in result.stdout.str()

def test_traceback_failure(testdir):
    p1 = testdir.makepyfile("""
        def g():
            return 2
        def f(x):
            assert x == g()
        def test_onefails():
            f(3)
    """)
    result = testdir.runpytest(p1)
    result.stdout.fnmatch_lines([
        "*test_traceback_failure.py F",
        "====* FAILURES *====",
        "____*____",
        "",
        "    def test_onefails():",
        ">       f(3)",
        "",
        "*test_*.py:6: ",
        "_ _ _ *",
        #"",
        "    def f(x):",
        ">       assert x == g()",
        "E       assert 3 == 2",
        "E        +  where 2 = g()",
        "",
        "*test_traceback_failure.py:4: AssertionError"
    ])

@pytest.mark.skipif("sys.version_info < (2,5) or '__pypy__' in sys.builtin_module_names or sys.platform.startswith('java')" )
def test_warn_missing(testdir):
    p1 = testdir.makepyfile("")
    result = testdir.run(sys.executable, "-OO", "-m", "pytest", "-h")
    result.stderr.fnmatch_lines([
        "*WARNING*assert statements are not executed*",
    ])
    result = testdir.run(sys.executable, "-OO", "-m", "pytest", "--no-assert")
    result.stderr.fnmatch_lines([
        "*WARNING*assert statements are not executed*",
    ])

def test_recursion_source_decode(testdir):
    testdir.makepyfile("""
        def test_something():
            pass
    """)
    testdir.makeini("""
        [pytest]
        python_files = *.py
    """)
    result = testdir.runpytest("--collectonly")
    result.stdout.fnmatch_lines("""
        <Module*>
    """)
