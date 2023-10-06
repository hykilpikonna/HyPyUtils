import requests


def setup_proxy(session: requests.Session, addr: str = 'socks5://localhost:9050', verbose: bool = True):
    url = 'https://ip.me'

    # Setup proxy
    ip = session.get(url).text.strip()
    session.proxies = {
        'http': addr,
        'https': addr
    }
    proxy_ip = session.get(url).text.strip()

    # Print ip
    if verbose:
        print(f'Raw ip: {ip}')
        print(f'Proxy ip: {proxy_ip}')

    # ips shouldn't match
    assert ip != proxy_ip, 'Proxy did not start correctly.'

    # Disable default requests behavior
    def warn(*args, **kwargs):
        raise ReferenceError('Use session.get instead of requests.get')
    requests.get = warn
    requests.post = warn
