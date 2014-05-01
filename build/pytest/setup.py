import os, sys
try:
    from setuptools import setup, Command
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Command

long_description = open("README.rst").read()
def main():
    setup(
        name='pytest',
        description='py.test: simple powerful testing with Python',
        long_description = long_description,
        version='2.3.5',
        url='http://pytest.org',
        license='MIT license',
        platforms=['unix', 'linux', 'osx', 'cygwin', 'win32'],
        author='Holger Krekel, Benjamin Peterson, Ronny Pfannschmidt, Floris Bruynooghe and others',
        author_email='holger at merlinux.eu',
        entry_points= make_entry_points(),
        cmdclass = {'test': PyTest},
        # the following should be enabled for release
        install_requires=['py>=1.4.13dev6'],
        classifiers=['Development Status :: 6 - Mature',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: POSIX',
                     'Operating System :: Microsoft :: Windows',
                     'Operating System :: MacOS :: MacOS X',
                     'Topic :: Software Development :: Testing',
                     'Topic :: Software Development :: Libraries',
                     'Topic :: Utilities',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 3'] + [
        ("Programming Language :: Python :: %s" % x) for x in
            "2.4 2.5 2.6 2.7 3.0 3.1 3.2 3.3".split()],
        packages=['_pytest', '_pytest.assertion'],
        py_modules=['pytest'],
        zip_safe=False,
    )

def cmdline_entrypoints(versioninfo, platform, basename):
    target = 'pytest:main'
    if platform.startswith('java'):
        points = {'py.test-jython': target}
    else:
        if basename.startswith("pypy"):
            points = {'py.test-%s' % basename: target}
        else: # cpython
            points = {'py.test-%s.%s' % versioninfo[:2] : target,}
        points['py.test'] = target
    return points

def make_entry_points():
    basename = os.path.basename(sys.executable)
    points = cmdline_entrypoints(sys.version_info, sys.platform, basename)
    keys = list(points.keys())
    keys.sort()
    l = ["%s = %s" % (x, points[x]) for x in keys]
    return {'console_scripts': l}


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        PPATH=[x for x in os.environ.get("PYTHONPATH", "").split(":") if x]
        PPATH.insert(0, os.getcwd())
        os.environ["PYTHONPATH"] = ":".join(PPATH)
        errno = subprocess.call([sys.executable, 'pytest.py'])
        raise SystemExit(errno)

if __name__ == '__main__':
    main()
