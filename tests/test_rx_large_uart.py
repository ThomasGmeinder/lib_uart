import xmostest
import os
from xmostest.xmostest_subprocess import call
from uart_rx_checker import UARTRxChecker, Parity


def do_test(baud, parity):
    myenv = {'baud':baud, 'parity':parity}
    path = "app_uart_test_rx_large"
    resources = xmostest.request_resource("xsim")

    checker = UARTRxChecker("tile[0]:XS1_PORT_1A", "tile[0]:XS1_PORT_1B", Parity[parity], baud, 4, 1, 8, range(256))
    tester  = xmostest.ComparisonTester(open('test_rx_large_uart.expect'),
                                        "lib_uart", "sim_regression", "rx_large", myenv,
                                        regexp=True)

    # Only want no parity @ 230400 baud for smoke tests
    if baud != 115200 or parity != 'UART_PARITY_NONE':
        tester.set_min_testlevel('nightly')
    if tester.test_required() != True:
        return

    xmostest.build(path, env = myenv, do_clean = True)

    xmostest.run_on_simulator(resources['xsim'],
        'app_uart_test_rx_large/bin/smoke/app_uart_test_rx_large_smoke.xe',
        simthreads = [checker],
        xscope_io=True,
        tester = tester,
        simargs = ["--vcd-tracing", "-tile tile[0] -ports -o trace.vcd"])

def runtests():
    for parity in ['UART_PARITY_EVEN', 'UART_PARITY_ODD', 'UART_PARITY_NONE']:
        for baud in [57600, 115200]:
            do_test(baud, parity)