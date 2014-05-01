from __future__ import division

__copyright__ = "Copyright (C) 2009 Andreas Kloeckner"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import numpy as np
import numpy.linalg as la
import pytools.test


import pyopencl as cl
import pyopencl.array as cl_array
from pyopencl.tools import (  # noqa
        pytest_generate_tests_for_pyopencl as pytest_generate_tests)

# Are CL implementations crashy? You be the judge. :)
try:
    import faulthandler  # noqa
except ImportError:
    pass
else:
    faulthandler.enable()


@pytools.test.mark_test.opencl
def test_get_info(platform, device):
    failure_count = [0]

    pocl_quirks = [
            (cl.Buffer, cl.mem_info.OFFSET),
            (cl.Program, cl.program_info.KERNEL_NAMES),
            (cl.Program, cl.program_info.NUM_KERNELS),
            ]
    CRASH_QUIRKS = [
            (("NVIDIA Corporation", "NVIDIA CUDA",
                "OpenCL 1.0 CUDA 3.0.1"),
                [
                    (cl.Event, cl.event_info.COMMAND_QUEUE),
                    ]),
            (("The pocl project", "Portable Computing Language",
                "OpenCL 1.2 pocl 0.8-pre"),
                    pocl_quirks),
            (("The pocl project", "Portable Computing Language",
                "OpenCL 1.2 pocl 0.8"),
                pocl_quirks),
            (("The pocl project", "Portable Computing Language",
                "OpenCL 1.2 pocl 0.9-pre"),
                pocl_quirks),
            (("Apple", "Apple",
                "OpenCL 1.2 (Apr 25 2013 18:32:06)"),
                [
                    (cl.Program, cl.program_info.SOURCE),
                    ]),
            ]
    QUIRKS = []

    plat_quirk_key = (
            platform.vendor,
            platform.name,
            platform.version)

    def find_quirk(quirk_list, cl_obj, info):
        for entry_plat_key, quirks in quirk_list:
            if entry_plat_key == plat_quirk_key:
                for quirk_cls, quirk_info in quirks:
                    if (isinstance(cl_obj, quirk_cls)
                            and quirk_info == info):
                        return True

        return False

    def do_test(cl_obj, info_cls, func=None, try_attr_form=True):
        if func is None:
            def func(info):
                cl_obj.get_info(info)

        for info_name in dir(info_cls):
            if not info_name.startswith("_") and info_name != "to_string":
                print(info_cls, info_name)
                info = getattr(info_cls, info_name)

                if find_quirk(CRASH_QUIRKS, cl_obj, info):
                    print("not executing get_info", type(cl_obj), info_name)
                    print("(known crash quirk for %s)" % platform.name)
                    continue

                try:
                    func(info)
                except:
                    msg = "failed get_info", type(cl_obj), info_name

                    if find_quirk(QUIRKS, cl_obj, info):
                        msg += ("(known quirk for %s)" % platform.name)
                    else:
                        failure_count[0] += 1

                if try_attr_form:
                    try:
                        getattr(cl_obj, info_name.lower())
                    except:
                        print("failed attr-based get_info", type(cl_obj), info_name)

                        if find_quirk(QUIRKS, cl_obj, info):
                            print("(known quirk for %s)" % platform.name)
                        else:
                            failure_count[0] += 1

    do_test(platform, cl.platform_info)

    do_test(device, cl.device_info)

    ctx = cl.Context([device])
    do_test(ctx, cl.context_info)

    props = 0
    if (device.queue_properties
            & cl.command_queue_properties.PROFILING_ENABLE):
        profiling = True
        props = cl.command_queue_properties.PROFILING_ENABLE
    queue = cl.CommandQueue(ctx,
            properties=props)
    do_test(queue, cl.command_queue_info)

    prg = cl.Program(ctx, """
        __kernel void sum(__global float *a)
        { a[get_global_id(0)] *= 2; }
        """).build()
    do_test(prg, cl.program_info)
    do_test(prg, cl.program_build_info,
            lambda info: prg.get_build_info(device, info),
            try_attr_form=False)

    n = 2000
    a_buf = cl.Buffer(ctx, 0, n*4)

    do_test(a_buf, cl.mem_info)

    kernel = prg.sum
    do_test(kernel, cl.kernel_info)

    evt = kernel(queue, (n,), None, a_buf)
    do_test(evt, cl.event_info)

    if profiling:
        evt.wait()
        do_test(evt, cl.profiling_info,
                lambda info: evt.get_profiling_info(info),
                try_attr_form=False)

    # crashes on intel...
    if device.image_support and platform.vendor not in [
            "Intel(R) Corporation",
            "The pocl project",
            ]:
        smp = cl.Sampler(ctx, False,
                cl.addressing_mode.CLAMP,
                cl.filter_mode.NEAREST)
        do_test(smp, cl.sampler_info)

        img_format = cl.get_supported_image_formats(
                ctx, cl.mem_flags.READ_ONLY, cl.mem_object_type.IMAGE2D)[0]

        img = cl.Image(ctx, cl.mem_flags.READ_ONLY, img_format, (128, 256))
        assert img.shape == (128, 256)

        img.depth
        img.image.depth
        do_test(img, cl.image_info,
                lambda info: img.get_image_info(info))


@pytools.test.mark_test.opencl
def test_invalid_kernel_names_cause_failures(ctx_factory):
    ctx = ctx_factory()
    device = ctx.devices[0]
    prg = cl.Program(ctx, """
        __kernel void sum(__global float *a)
        { a[get_global_id(0)] *= 2; }
        """).build()

    if ctx.devices[0].platform.vendor == "The pocl project":
        # https://bugs.launchpad.net/pocl/+bug/1184464

        import pytest
        pytest.skip("pocl doesn't like invalid kernel names")

    try:
        prg.sam
        raise RuntimeError("invalid kernel name did not cause error")
    except AttributeError:
        pass
    except RuntimeError:
        if "Intel" in device.platform.vendor:
            from pytest import xfail
            xfail("weird exception from OpenCL implementation "
                    "on invalid kernel name--are you using "
                    "Intel's implementation? (if so, known bug in Intel CL)")
        else:
            raise


@pytools.test.mark_test.opencl
def test_image_format_constructor():
    # doesn't need image support to succeed
    iform = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.FLOAT)

    assert iform.channel_order == cl.channel_order.RGBA
    assert iform.channel_data_type == cl.channel_type.FLOAT
    assert not iform.__dict__


@pytools.test.mark_test.opencl
def test_nonempty_supported_image_formats(ctx_factory):
    context = ctx_factory()

    device = context.devices[0]

    if device.image_support:
        assert len(cl.get_supported_image_formats(
                context, cl.mem_flags.READ_ONLY, cl.mem_object_type.IMAGE2D)) > 0
    else:
        from pytest import skip
        skip("images not supported on %s" % device.name)


@pytools.test.mark_test.opencl
def test_that_python_args_fail(ctx_factory):
    context = ctx_factory()

    prg = cl.Program(context, """
        __kernel void mult(__global float *a, float b, int c)
        { a[get_global_id(0)] *= (b+c); }
        """).build()

    a = np.random.rand(50000)
    queue = cl.CommandQueue(context)
    mf = cl.mem_flags
    a_buf = cl.Buffer(context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=a)

    knl = cl.Kernel(prg, "mult")
    try:
        knl(queue, a.shape, None, a_buf, 2, 3)
        assert False, "PyOpenCL should not accept bare Python types as arguments"
    except cl.LogicError:
        pass

    try:
        prg.mult(queue, a.shape, None, a_buf, float(2), 3)
        assert False, "PyOpenCL should not accept bare Python types as arguments"
    except cl.LogicError:
        pass

    prg.mult(queue, a.shape, None, a_buf, np.float32(2), np.int32(3))

    a_result = np.empty_like(a)
    cl.enqueue_read_buffer(queue, a_buf, a_result).wait()


@pytools.test.mark_test.opencl
def test_image_2d(ctx_factory):
    context = ctx_factory()

    device, = context.devices

    if not device.image_support:
        from pytest import skip
        skip("images not supported on %s" % device)

    if "Intel" in device.vendor and "31360.31426" in device.version:
        from pytest import skip
        skip("images crashy on %s" % device)
    if "pocl" in device.platform.vendor and (
            "0.8" in device.platform.version or
            "0.9" in device.platform.version
            ):
        from pytest import skip
        skip("images crashy on %s" % device)

    prg = cl.Program(context, """
        __kernel void copy_image(
          __global float *dest,
          __read_only image2d_t src,
          sampler_t samp,
          int stride0)
        {
          int d0 = get_global_id(0);
          int d1 = get_global_id(1);
          /*
          const sampler_t samp =
            CLK_NORMALIZED_COORDS_FALSE
            | CLK_ADDRESS_CLAMP
            | CLK_FILTER_NEAREST;
            */
          dest[d0*stride0 + d1] = read_imagef(src, samp, (float2)(d1, d0)).x;
        }
        """).build()

    num_channels = 1
    a = np.random.rand(1024, 512, num_channels).astype(np.float32)
    if num_channels == 1:
        a = a[:, :, 0]

    queue = cl.CommandQueue(context)
    try:
        a_img = cl.image_from_array(context, a, num_channels)
    except cl.RuntimeError:
        import sys
        exc = sys.exc_info()[1]
        if exc.code == cl.status_code.IMAGE_FORMAT_NOT_SUPPORTED:
            from pytest import skip
            skip("required image format not supported on %s" % device.name)
        else:
            raise

    a_dest = cl.Buffer(context, cl.mem_flags.READ_WRITE, a.nbytes)

    samp = cl.Sampler(context, False,
            cl.addressing_mode.CLAMP,
            cl.filter_mode.NEAREST)
    prg.copy_image(queue, a.shape, None, a_dest, a_img, samp,
            np.int32(a.strides[0]/a.dtype.itemsize))

    a_result = np.empty_like(a)
    cl.enqueue_copy(queue, a_result, a_dest)

    good = la.norm(a_result - a) == 0
    if not good:
        if queue.device.type & cl.device_type.CPU:
            assert good, ("The image implementation on your CPU CL platform '%s' "
                    "returned bad values. This is bad, but common."
                    % queue.device.platform)
        else:
            assert good


@pytools.test.mark_test.opencl
def test_image_3d(ctx_factory):
    #test for image_from_array for 3d image of float2
    context = ctx_factory()

    device, = context.devices

    if not device.image_support:
        from pytest import skip
        skip("images not supported on %s" % device)

    if device.platform.vendor == "Intel(R) Corporation":
        from pytest import skip
        skip("images crashy on %s" % device)

    prg = cl.Program(context, """
        __kernel void copy_image_plane(
          __global float2 *dest,
          __read_only image3d_t src,
          sampler_t samp,
          int stride0,
          int stride1)
        {
          int d0 = get_global_id(0);
          int d1 = get_global_id(1);
          int d2 = get_global_id(2);
          /*
          const sampler_t samp =
            CLK_NORMALIZED_COORDS_FALSE
            | CLK_ADDRESS_CLAMP
            | CLK_FILTER_NEAREST;
            */
          dest[d0*stride0 + d1*stride1 + d2] = read_imagef(
                src, samp, (float4)(d2, d1, d0, 0)).xy;
        }
        """).build()

    num_channels = 2
    shape = (3, 4, 2)
    a = np.random.random(shape + (num_channels,)).astype(np.float32)

    queue = cl.CommandQueue(context)
    try:
        a_img = cl.image_from_array(context, a, num_channels)
    except cl.RuntimeError:
        import sys
        exc = sys.exc_info()[1]
        if exc.code == cl.status_code.IMAGE_FORMAT_NOT_SUPPORTED:
            from pytest import skip
            skip("required image format not supported on %s" % device.name)
        else:
            raise

    a_dest = cl.Buffer(context, cl.mem_flags.READ_WRITE, a.nbytes)

    samp = cl.Sampler(context, False,
            cl.addressing_mode.CLAMP,
            cl.filter_mode.NEAREST)
    prg.copy_image_plane(queue, shape, None, a_dest, a_img, samp,
                         np.int32(a.strides[0]/a.itemsize/num_channels),
                         np.int32(a.strides[1]/a.itemsize/num_channels),
                         )

    a_result = np.empty_like(a)
    cl.enqueue_copy(queue, a_result, a_dest)

    good = la.norm(a_result - a) == 0
    if not good:
        if queue.device.type & cl.device_type.CPU:
            assert good, ("The image implementation on your CPU CL platform '%s' "
                    "returned bad values. This is bad, but common."
                    % queue.device.platform)
        else:
            assert good


@pytools.test.mark_test.opencl
def test_copy_buffer(ctx_factory):
    context = ctx_factory()

    queue = cl.CommandQueue(context)
    mf = cl.mem_flags

    a = np.random.rand(50000).astype(np.float32)
    b = np.empty_like(a)

    buf1 = cl.Buffer(context, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=a)
    buf2 = cl.Buffer(context, mf.WRITE_ONLY, b.nbytes)

    cl.enqueue_copy_buffer(queue, buf1, buf2).wait()
    cl.enqueue_read_buffer(queue, buf2, b).wait()

    assert la.norm(a - b) == 0


@pytools.test.mark_test.opencl
def test_mempool(ctx_factory):
    from pyopencl.tools import MemoryPool, CLAllocator

    context = ctx_factory()

    pool = MemoryPool(CLAllocator(context))
    maxlen = 10
    queue = []

    e0 = 12

    for e in range(e0-6, e0-4):
        for i in range(100):
            queue.append(pool.allocate(1<<e))
            if len(queue) > 10:
                queue.pop(0)
    del queue
    pool.stop_holding()

@pytools.test.mark_test.opencl
def test_mempool_2():
    from pyopencl.tools import MemoryPool
    from random import randrange

    for i in range(2000):
        s = randrange(1<<31) >> randrange(32)
        bin_nr = MemoryPool.bin_number(s)
        asize = MemoryPool.alloc_size(bin_nr)

        assert asize >= s, s
        assert MemoryPool.bin_number(asize) == bin_nr, s
        assert asize < asize*(1+1/8)

@pytools.test.mark_test.opencl
def test_vector_args(ctx_factory):
    context = ctx_factory()
    queue = cl.CommandQueue(context)

    prg = cl.Program(context, """
        __kernel void set_vec(float4 x, __global float4 *dest)
        { dest[get_global_id(0)] = x; }
        """).build()

    x = cl_array.vec.make_float4(1,2,3,4)
    dest = np.empty(50000, cl_array.vec.float4)
    mf = cl.mem_flags
    dest_buf = cl.Buffer(context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=dest)

    prg.set_vec(queue, dest.shape, None, x, dest_buf)

    cl.enqueue_read_buffer(queue, dest_buf, dest).wait()

    assert (dest == x).all()

@pytools.test.mark_test.opencl
def test_header_dep_handling(ctx_factory):
    context = ctx_factory()

    from os.path import exists
    assert exists("empty-header.h") # if this fails, change dir to pyopencl/test

    kernel_src = """
    #include <empty-header.h>
    kernel void zonk(global int *a)
    {
      *a = 5;
    }
    """

    import os

    cl.Program(context, kernel_src).build(["-I", os.getcwd()])
    cl.Program(context, kernel_src).build(["-I", os.getcwd()])

@pytools.test.mark_test.opencl
def test_context_dep_memoize(ctx_factory):
    context = ctx_factory()

    from pyopencl.tools import context_dependent_memoize

    counter = [0]

    @context_dependent_memoize
    def do_something(ctx):
        counter[0] += 1

    do_something(context)
    do_something(context)

    assert counter[0] == 1

@pytools.test.mark_test.opencl
def test_can_build_binary(ctx_factory):
    ctx = ctx_factory()
    device, = ctx.devices

    program = cl.Program(ctx, """
    __kernel void simple(__global float *in, __global float *out)
    {
        out[get_global_id(0)] = in[get_global_id(0)];
    }""")
    program.build()
    binary = program.get_info(cl.program_info.BINARIES)[0]

    foo = cl.Program(ctx, [device], [binary])
    foo.build()




if __name__ == "__main__":
    # make sure that import failures get reported, instead of skipping the tests.
    import pyopencl

    import sys
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from py.test.cmdline import main
        main([__file__])
