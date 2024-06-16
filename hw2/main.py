import argparse
import logging
import os
import subprocess
import platform

RIGHT_BORDER = 1491
ADD_VAL = 28


def get_cmd(platform : str, mtu : int, host: str, count : int) -> list:
    if platform == 'darwin':
        return ["ping", "-D", "-s", str(mtu), host, "-c", str(count), "-W", "3000"]
    return ["ping", host, "-c", str(count), "-s", str(mtu), "-M", "do"]

def ping(mtu : int, host : str, count : int):
    print(mtu, host, count)
    cmd = get_cmd(platform.system().lower(), mtu, host, count)
    print(cmd)
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    if res.returncode == 2:
        exit(2)
    return int(res.returncode != 0), "", res.stderr


def worker(ping_count: int,  verb_mode: str, host: str) -> None:
    res = process(ping_count, verb_mode, host)
    print("ANSWER =", res)

def perfrom_binsearch(host : str, cnt : int, l : int = 0, r : int= RIGHT_BORDER) -> int:
    while l < r - 1:
        m = (l + r) // 2
        res = ping(m, host, cnt)
        code, out, err = res
        if code == 1:
            r = m
            continue
        if code == 0:
            l = m
            continue
        logging.error(err)
    return l + ADD_VAL


def process(ping_count: int, verb_mode: str, host: str) -> int:
    cnt = int(ping_count)
    if verb_mode == '1':
        logging.info("verbose on")

    reachable = True if os.system("ping -c 1 " + host) is 0 else False
    if not reachable:
        exit(2)

    disabled = subprocess.run(
        ["cat", "/proc/sys/net/ipv4/icmp_echo_ignore_all"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if disabled.stdout == 1:
        print('ICMP is disabled. Enable it')
        exit(1)
    return perfrom_binsearch(host, cnt)
    


parser = argparse.ArgumentParser(description='PMTUD')
parser.add_argument('-cnt', default=1, help='count of pings')
parser.add_argument('-verbose', default=0, help='verbose mod')
parser.add_argument('host', help='host')

args = parser.parse_args()

host = args.host
count = args.cnt
verbose = args.verbose

if __name__ == "__main__":
    worker(ping_count=count, verb_mode=verbose, host=host)