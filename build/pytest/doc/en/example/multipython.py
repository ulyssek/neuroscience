"""
module containing a parametrized tests testing cross-python
serialization via the pickle module.
"""
import py, pytest

pythonlist = ['python2.4', 'python2.5', 'python2.6', 'python2.7', 'python2.8']
@pytest.fixture(params=pythonlist)
def python1(request, tmpdir):
    picklefile = tmpdir.join("data.pickle")
    return Python(request.param, picklefile)

@pytest.fixture(params=pythonlist)
def python2(request, python1):
    return Python(request.param, python1.picklefile)

class Python:
    def __init__(self, version, picklefile):
        self.pythonpath = py.path.local.sysfind(version)
        if not self.pythonpath:
            py.test.skip("%r not found" %(version,))
        self.picklefile = picklefile
    def dumps(self, obj):
        dumpfile = self.picklefile.dirpath("dump.py")
        dumpfile.write(py.code.Source("""
            import pickle
            f = open(%r, 'wb')
            s = pickle.dump(%r, f)
            f.close()
        """ % (str(self.picklefile), obj)))
        py.process.cmdexec("%s %s" %(self.pythonpath, dumpfile))

    def load_and_is_true(self, expression):
        loadfile = self.picklefile.dirpath("load.py")
        loadfile.write(py.code.Source("""
            import pickle
            f = open(%r, 'rb')
            obj = pickle.load(f)
            f.close()
            res = eval(%r)
            if not res:
                raise SystemExit(1)
        """ % (str(self.picklefile), expression)))
        print (loadfile)
        py.process.cmdexec("%s %s" %(self.pythonpath, loadfile))

@pytest.mark.parametrize("obj", [42, {}, {1:3},])
def test_basic_objects(python1, python2, obj):
    python1.dumps(obj)
    python2.load_and_is_true("obj == %s" % obj)
