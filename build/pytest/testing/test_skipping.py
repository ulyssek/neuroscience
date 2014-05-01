import pytest
import sys

from _pytest.skipping import MarkEvaluator, folded_skips
from _pytest.skipping import pytest_runtest_setup
from _pytest.runner import runtestprotocol

class TestEvaluator:
    def test_no_marker(self, testdir):
        item = testdir.getitem("def test_func(): pass")
        evalskipif = MarkEvaluator(item, 'skipif')
        assert not evalskipif
        assert not evalskipif.istrue()

    def test_marked_no_args(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.xyz
            def test_func():
                pass
        """)
        ev = MarkEvaluator(item, 'xyz')
        assert ev
        assert ev.istrue()
        expl = ev.getexplanation()
        assert expl == ""
        assert not ev.get("run", False)

    def test_marked_one_arg(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.xyz("hasattr(os, 'sep')")
            def test_func():
                pass
        """)
        ev = MarkEvaluator(item, 'xyz')
        assert ev
        assert ev.istrue()
        expl = ev.getexplanation()
        assert expl == "condition: hasattr(os, 'sep')"

    @pytest.mark.skipif('sys.version_info[0] >= 3')
    def test_marked_one_arg_unicode(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.xyz(u"hasattr(os, 'sep')")
            def test_func():
                pass
        """)
        ev = MarkEvaluator(item, 'xyz')
        assert ev
        assert ev.istrue()
        expl = ev.getexplanation()
        assert expl == "condition: hasattr(os, 'sep')"

    def test_marked_one_arg_with_reason(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.xyz("hasattr(os, 'sep')", attr=2, reason="hello world")
            def test_func():
                pass
        """)
        ev = MarkEvaluator(item, 'xyz')
        assert ev
        assert ev.istrue()
        expl = ev.getexplanation()
        assert expl == "hello world"
        assert ev.get("attr") == 2

    def test_marked_one_arg_twice(self, testdir):
        lines = [
            '''@pytest.mark.skipif("not hasattr(os, 'murks')")''',
            '''@pytest.mark.skipif("hasattr(os, 'murks')")'''
        ]
        for i in range(0, 2):
            item = testdir.getitem("""
                import pytest
                %s
                %s
                def test_func():
                    pass
            """ % (lines[i], lines[(i+1) %2]))
            ev = MarkEvaluator(item, 'skipif')
            assert ev
            assert ev.istrue()
            expl = ev.getexplanation()
            assert expl == "condition: not hasattr(os, 'murks')"

    def test_marked_one_arg_twice2(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.skipif("hasattr(os, 'murks')")
            @pytest.mark.skipif("not hasattr(os, 'murks')")
            def test_func():
                pass
        """)
        ev = MarkEvaluator(item, 'skipif')
        assert ev
        assert ev.istrue()
        expl = ev.getexplanation()
        assert expl == "condition: not hasattr(os, 'murks')"

    def test_skipif_class(self, testdir):
        item, = testdir.getitems("""
            import pytest
            class TestClass:
                pytestmark = pytest.mark.skipif("config._hackxyz")
                def test_func(self):
                    pass
        """)
        item.config._hackxyz = 3
        ev = MarkEvaluator(item, 'skipif')
        assert ev.istrue()
        expl = ev.getexplanation()
        assert expl == "condition: config._hackxyz"


class TestXFail:
    def test_xfail_simple(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.xfail
            def test_func():
                assert 0
        """)
        reports = runtestprotocol(item, log=False)
        assert len(reports) == 3
        callreport = reports[1]
        assert callreport.skipped
        assert callreport.wasxfail == ""

    def test_xfail_xpassed(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.xfail
            def test_func():
                assert 1
        """)
        reports = runtestprotocol(item, log=False)
        assert len(reports) == 3
        callreport = reports[1]
        assert callreport.failed
        assert callreport.wasxfail == ""

    def test_xfail_run_anyway(self, testdir):
        testdir.makepyfile("""
            import pytest
            @pytest.mark.xfail
            def test_func():
                assert 0
        """)
        result = testdir.runpytest("--runxfail")
        assert result.ret == 1
        result.stdout.fnmatch_lines([
            "*def test_func():*",
            "*assert 0*",
            "*1 failed*",
        ])

    def test_xfail_evalfalse_but_fails(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.xfail('False')
            def test_func():
                assert 0
        """)
        reports = runtestprotocol(item, log=False)
        callreport = reports[1]
        assert callreport.failed
        assert not hasattr(callreport, "wasxfail")
        assert 'xfail' in callreport.keywords

    def test_xfail_not_report_default(self, testdir):
        p = testdir.makepyfile(test_one="""
            import pytest
            @pytest.mark.xfail
            def test_this():
                assert 0
        """)
        result = testdir.runpytest(p, '-v')
        #result.stdout.fnmatch_lines([
        #    "*HINT*use*-r*"
        #])

    def test_xfail_not_run_xfail_reporting(self, testdir):
        p = testdir.makepyfile(test_one="""
            import pytest
            @pytest.mark.xfail(run=False, reason="noway")
            def test_this():
                assert 0
            @pytest.mark.xfail("True", run=False)
            def test_this_true():
                assert 0
            @pytest.mark.xfail("False", run=False, reason="huh")
            def test_this_false():
                assert 1
        """)
        result = testdir.runpytest(p, '--report=xfailed', )
        result.stdout.fnmatch_lines([
            "*test_one*test_this*",
            "*NOTRUN*noway",
            "*test_one*test_this_true*",
            "*NOTRUN*condition:*True*",
            "*1 passed*",
        ])

    def test_xfail_not_run_no_setup_run(self, testdir):
        p = testdir.makepyfile(test_one="""
            import pytest
            @pytest.mark.xfail(run=False, reason="hello")
            def test_this():
                assert 0
            def setup_module(mod):
                raise ValueError(42)
        """)
        result = testdir.runpytest(p, '--report=xfailed', )
        result.stdout.fnmatch_lines([
            "*test_one*test_this*",
            "*NOTRUN*hello",
            "*1 xfailed*",
        ])

    def test_xfail_xpass(self, testdir):
        p = testdir.makepyfile(test_one="""
            import pytest
            @pytest.mark.xfail
            def test_that():
                assert 1
        """)
        result = testdir.runpytest(p, '-rX')
        result.stdout.fnmatch_lines([
            "*XPASS*test_that*",
            "*1 xpassed*"
        ])
        assert result.ret == 0

    def test_xfail_imperative(self, testdir):
        p = testdir.makepyfile("""
            import pytest
            def test_this():
                pytest.xfail("hello")
        """)
        result = testdir.runpytest(p)
        result.stdout.fnmatch_lines([
            "*1 xfailed*",
        ])
        result = testdir.runpytest(p, "-rx")
        result.stdout.fnmatch_lines([
            "*XFAIL*test_this*",
            "*reason:*hello*",
        ])
        result = testdir.runpytest(p, "--runxfail")
        result.stdout.fnmatch_lines([
            "*def test_this():*",
            "*pytest.xfail*",
        ])

    def test_xfail_imperative_in_setup_function(self, testdir):
        p = testdir.makepyfile("""
            import pytest
            def setup_function(function):
                pytest.xfail("hello")

            def test_this():
                assert 0
        """)
        result = testdir.runpytest(p)
        result.stdout.fnmatch_lines([
            "*1 xfailed*",
        ])
        result = testdir.runpytest(p, "-rx")
        result.stdout.fnmatch_lines([
            "*XFAIL*test_this*",
            "*reason:*hello*",
        ])
        result = testdir.runpytest(p, "--runxfail")
        result.stdout.fnmatch_lines([
            "*def setup_function(function):*",
            "*pytest.xfail*",
        ])

    def xtest_dynamic_xfail_set_during_setup(self, testdir):
        p = testdir.makepyfile("""
            import pytest
            def setup_function(function):
                pytest.mark.xfail(function)
            def test_this():
                assert 0
            def test_that():
                assert 1
        """)
        result = testdir.runpytest(p, '-rxX')
        result.stdout.fnmatch_lines([
            "*XFAIL*test_this*",
            "*XPASS*test_that*",
        ])

    def test_dynamic_xfail_no_run(self, testdir):
        p = testdir.makepyfile("""
            import pytest
            def pytest_funcarg__arg(request):
                request.applymarker(pytest.mark.xfail(run=False))
            def test_this(arg):
                assert 0
        """)
        result = testdir.runpytest(p, '-rxX')
        result.stdout.fnmatch_lines([
            "*XFAIL*test_this*",
            "*NOTRUN*",
        ])

    def test_dynamic_xfail_set_during_funcarg_setup(self, testdir):
        p = testdir.makepyfile("""
            import pytest
            def pytest_funcarg__arg(request):
                request.applymarker(pytest.mark.xfail)
            def test_this2(arg):
                assert 0
        """)
        result = testdir.runpytest(p)
        result.stdout.fnmatch_lines([
            "*1 xfailed*",
        ])

class TestXFailwithSetupTeardown:
    def test_failing_setup_issue9(self, testdir):
        testdir.makepyfile("""
            import pytest
            def setup_function(func):
                assert 0

            @pytest.mark.xfail
            def test_func():
                pass
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "*1 xfail*",
        ])

    def test_failing_teardown_issue9(self, testdir):
        testdir.makepyfile("""
            import pytest
            def teardown_function(func):
                assert 0

            @pytest.mark.xfail
            def test_func():
                pass
        """)
        result = testdir.runpytest()
        result.stdout.fnmatch_lines([
            "*1 xfail*",
        ])


class TestSkipif:
    def test_skipif_conditional(self, testdir):
        item = testdir.getitem("""
            import pytest
            @pytest.mark.skipif("hasattr(os, 'sep')")
            def test_func():
                pass
        """)
        x = pytest.raises(pytest.skip.Exception, "pytest_runtest_setup(item)")
        assert x.value.msg == "condition: hasattr(os, 'sep')"


    def test_skipif_reporting(self, testdir):
        p = testdir.makepyfile("""
            import pytest
            @pytest.mark.skipif("hasattr(sys, 'platform')")
            def test_that():
                assert 0
        """)
        result = testdir.runpytest(p, '-s', '-rs')
        result.stdout.fnmatch_lines([
            "*SKIP*1*platform*",
            "*1 skipped*"
        ])
        assert result.ret == 0

def test_skip_not_report_default(testdir):
    p = testdir.makepyfile(test_one="""
        import pytest
        def test_this():
            pytest.skip("hello")
    """)
    result = testdir.runpytest(p, '-v')
    result.stdout.fnmatch_lines([
        #"*HINT*use*-r*",
        "*1 skipped*",
    ])


def test_skipif_class(testdir):
    p = testdir.makepyfile("""
        import pytest

        class TestClass:
            pytestmark = pytest.mark.skipif("True")
            def test_that(self):
                assert 0
            def test_though(self):
                assert 0
    """)
    result = testdir.runpytest(p)
    result.stdout.fnmatch_lines([
        "*2 skipped*"
    ])


def test_skip_reasons_folding():
    path = 'xyz'
    lineno = 3
    message = "justso"
    longrepr = (path, lineno, message)

    class X:
        pass
    ev1 = X()
    ev1.when = "execute"
    ev1.skipped = True
    ev1.longrepr = longrepr

    ev2 = X()
    ev2.longrepr = longrepr
    ev2.skipped = True

    l = folded_skips([ev1, ev2])
    assert len(l) == 1
    num, fspath, lineno, reason = l[0]
    assert num == 2
    assert fspath == path
    assert lineno == lineno
    assert reason == message

def test_skipped_reasons_functional(testdir):
    testdir.makepyfile(
        test_one="""
            from conftest import doskip
            def setup_function(func):
                doskip()
            def test_func():
                pass
            class TestClass:
                def test_method(self):
                    doskip()
       """,
       test_two = """
            from conftest import doskip
            doskip()
       """,
       conftest = """
            import pytest
            def doskip():
                pytest.skip('test')
        """
    )
    result = testdir.runpytest('--report=skipped')
    result.stdout.fnmatch_lines([
        "*SKIP*3*conftest.py:3: test",
    ])
    assert result.ret == 0

def test_reportchars(testdir):
    testdir.makepyfile("""
        import pytest
        def test_1():
            assert 0
        @pytest.mark.xfail
        def test_2():
            assert 0
        @pytest.mark.xfail
        def test_3():
            pass
        def test_4():
            pytest.skip("four")
    """)
    result = testdir.runpytest("-rfxXs")
    result.stdout.fnmatch_lines([
        "FAIL*test_1*",
        "XFAIL*test_2*",
        "XPASS*test_3*",
        "SKIP*four*",
    ])

def test_reportchars_error(testdir):
    testdir.makepyfile(
        conftest="""
        def pytest_runtest_teardown():
            assert 0
        """,
        test_simple="""
        def test_foo():
            pass
        """)
    result = testdir.runpytest('-rE')
    result.stdout.fnmatch_lines([
        'ERROR*test_foo*',
    ])

@pytest.mark.xfail("hasattr(sys, 'pypy_version_info')")
def test_errors_in_xfail_skip_expressions(testdir):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.skipif("asd")
        def test_nameerror():
            pass
        @pytest.mark.xfail("syntax error")
        def test_syntax():
            pass

        def test_func():
            pass
    """)
    result = testdir.runpytest()
    markline = "                ^"
    if sys.platform.startswith("java"):
        # XXX report this to java
        markline = "*" + markline[8:]
    result.stdout.fnmatch_lines([
        "*ERROR*test_nameerror*",
        "*evaluating*skipif*expression*",
        "*asd*",
        "*ERROR*test_syntax*",
        "*evaluating*xfail*expression*",
        "    syntax error",
        markline,
        "SyntaxError: invalid syntax",
        "*1 pass*2 error*",
    ])

def test_xfail_skipif_with_globals(testdir):
    testdir.makepyfile("""
        import pytest
        x = 3
        @pytest.mark.skipif("x == 3")
        def test_skip1():
            pass
        @pytest.mark.xfail("x == 3")
        def test_boolean():
            assert 0
    """)
    result = testdir.runpytest("-rsx")
    result.stdout.fnmatch_lines([
        "*SKIP*x == 3*",
        "*XFAIL*test_boolean*",
        "*x == 3*",
    ])

def test_direct_gives_error(testdir):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.skipif(True)
        def test_skip1():
            pass
    """)
    result = testdir.runpytest()
    result.stdout.fnmatch_lines([
        "*1 error*",
    ])


def test_default_markers(testdir):
    result = testdir.runpytest("--markers")
    result.stdout.fnmatch_lines([
        "*skipif(*condition)*skip*",
        "*xfail(*condition, reason=None, run=True)*expected failure*",
    ])


def test_xfail_test_setup_exception(testdir):
    testdir.makeconftest("""
            def pytest_runtest_setup():
                0 / 0
        """)
    p = testdir.makepyfile("""
            import pytest
            @pytest.mark.xfail
            def test_func():
                assert 0
        """)
    result = testdir.runpytest(p)
    assert result.ret == 0
    assert 'xfailed' in result.stdout.str()
    assert 'xpassed' not in result.stdout.str()

def test_imperativeskip_on_xfail_test(testdir):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.xfail
        def test_that_fails():
            assert 0

        @pytest.mark.skipif("True")
        def test_hello():
            pass
    """)
    testdir.makeconftest("""
        import pytest
        def pytest_runtest_setup(item):
            pytest.skip("abc")
    """)
    result = testdir.runpytest("-rsxX")
    result.stdout.fnmatch_lines_random("""
        *SKIP*abc*
        *SKIP*condition: True*
        *2 skipped*
    """)


