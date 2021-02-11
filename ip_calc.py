"""Module for getting information about IP addresses"""

from typing import List

FULL_BYTE = 0b11111111


def get_ip_from_raw_address(raw_address: str) -> str:
    """
    Return IP address from the given raw address.

    >>> get_ip_from_raw_address('91.124.230.205/30')
    '91.124.230.205'
    >>> get_ip_from_raw_address('192.168.1.15/24')
    '192.168.1.15'
    """
    return raw_address.rsplit('/')[0]


def get_network_address_from_raw_address(raw_address: str) -> str:
    """
    Return network address from the given raw address.

    >>> get_network_address_from_raw_address('91.124.230.205/30')
    '91.124.230.204'
    >>> get_network_address_from_raw_address('91.124.230.205/32')
    '91.124.230.205'
    >>> get_network_address_from_raw_address('91.124.230.205/3')
    '64.0.0.0'
    """
    ip_address = split_address(raw_address)
    mask = get_network_mask(raw_address)
    network_address = [0, 0, 0, 0]

    for idx in range(4):
        network_address[idx] = ip_address[idx] & mask[idx]

    return join_address(network_address)


def get_broadcast_address_from_raw_address(raw_address: str) -> str:
    """
    Return broadcast address from the given raw address.

    >>> get_broadcast_address_from_raw_address('91.124.230.205/30')
    '91.124.230.207'
    """
    ip_address = split_address(get_ip_from_raw_address(raw_address))
    network_mask = get_network_mask(raw_address)
    broadcast_mask = invert_address(network_mask)

    broadcast_address = []

    for idx, byte in enumerate(ip_address):
        broadcast_address.append(byte | broadcast_mask[idx])

    return join_address(broadcast_address)


def get_binary_mask_from_raw_address(raw_address: str) -> str:
    """
    Get binary subnet mask from the given raw address.

    >>> get_binary_mask_from_raw_address('91.124.230.205/30')
    '11111111.11111111.11111111.11111100'
    >>> get_binary_mask_from_raw_address('91.124.230.205/25')
    '11111111.11111111.11111111.10000000'
    >>> get_binary_mask_from_raw_address('91.124.230.205/1')
    '10000000.00000000.00000000.00000000'
    """
    network_mask = get_network_mask(raw_address)

    network_binary_mask = ['{:08b}'.format(byte) for byte in network_mask]

    return join_address(network_binary_mask)


def get_first_usable_ip_address_from_raw_address(raw_address: str) -> str:
    """
    Get first usable IP address from the given raw address.

    >>> get_first_usable_ip_address_from_raw_address('91.124.230.205/30')
    '91.124.230.205'
    >>> get_first_usable_ip_address_from_raw_address('91.124.230.205/32')
    '91.124.230.206'
    >>> get_first_usable_ip_address_from_raw_address('91.124.230.205/3')
    '64.0.0.1'
    """
    network_address_str = get_network_address_from_raw_address(raw_address)
    network_address = split_address(network_address_str)

    # First usable IP address is the next one after network address
    network_address[-1] += 1

    return join_address(network_address)


def get_penultimate_usable_ip_address_from_raw_address(raw_address: str) -> str:
    """
    Get penultimate usable IP address from raw address.

    >>> get_penultimate_usable_ip_address_from_raw_address('91.124.230.205/30')
    '91.124.230.205'
    >>> get_penultimate_usable_ip_address_from_raw_address('215.017.125.177/28')
    '215.17.125.189'
    """
    broadcast_address = split_address(
        get_broadcast_address_from_raw_address(raw_address))

    # Change the last bit of broadcast address to 0
    broadcast_address[-1] -= 1

    penultimate_ip = []

    for idx, byte in enumerate(broadcast_address):
        penultimate_ip.append(
            (byte | broadcast_address[idx]) & broadcast_address[idx])

    # Switch from the last usable IP to the penultimate one
    penultimate_ip[-1] -= 1

    return join_address(penultimate_ip)


def get_number_of_usable_hosts_from_raw_address(raw_address: str) -> int:
    """
    Get the number of usable hosts from the given raw address.

    >>> get_number_of_usable_hosts_from_raw_address('91.124.230.205/8')
    16777214
    >>> get_number_of_usable_hosts_from_raw_address('91.124.230.205/16')
    65534
    >>> get_number_of_usable_hosts_from_raw_address('91.124.230.205/24')
    254
    >>> get_number_of_usable_hosts_from_raw_address('91.124.230.205/29')
    6
    """
    num_network_bits = int(raw_address.rsplit('/')[1])

    return 2 ** (32 - num_network_bits) - 2


def get_ip_class_from_raw_address(raw_address: str) -> str:
    """
    Get the class of the IP address from the given raw address (one of 'A', 'B', 'C', 'D', 'E').

    'A': 1.0.0.0 to 126.0.0.0
    'B': 128.0.0.0 to 191.255.0.0
    'C': 192.0.0.0 to 223.255.255.0
    'D': 224.0.0.0 to 239.255.255.255
    'E': 240.0.0.0 to 247.255.255.255

    >>> get_ip_class_from_raw_address('91.124.230.205/30')
    'A'
    >>> get_ip_class_from_raw_address('225.124.230.205/30')
    'D'
    """
    ip_address = split_address(raw_address)

    if 1 <= ip_address[0] <= 126:
        return 'A'

    if 128 <= ip_address[0] <= 191:
        return 'B'

    if 192 <= ip_address[0] <= 223:
        return 'C'

    if 224 <= ip_address[0] <= 239:
        return 'D'

    if 240 <= ip_address[0] <= 247:
        return 'E'

    return 'Unknown class'


def check_private_ip_address_from_raw_address(raw_address: str) -> bool:
    """
    Check if IP address is private given the raw address.

    Private IP addresses blocks:
    - 10.0.0.0 to 10.255.255.255
    - 172.16.0.0 to 172.31.255.255
    - 192.168.0.0 to 192.168.255.255

    >>> check_private_ip_address_from_raw_address('172.25.255.255/8')
    True
    >>> check_private_ip_address_from_raw_address('10.205.13.24/8')
    True
    >>> check_private_ip_address_from_raw_address('192.168.32.45/8')
    True
    >>> check_private_ip_address_from_raw_address('172.32.0.0/8')
    False
    """
    ip_address = split_address(raw_address)

    is_first_block = ip_address[0] == 10
    is_second_block = ip_address[0] == 172 and 16 <= ip_address[1] <= 31
    is_third_block = ip_address[:2] == [192, 168]

    return is_first_block or is_second_block or is_third_block


def get_network_mask(raw_address) -> List[int]:
    """
    Return a network mask from the given raw address.

    >>> get_network_mask('0.0.0.0/8')
    [255, 0, 0, 0]
    >>> get_network_mask('0.0.0.0/9')
    [255, 128, 0, 0]
    >>> get_network_mask('0.0.0.0/32')
    [255, 255, 255, 255]
    """
    num_bits = int(raw_address.rsplit('/')[1])
    mask = [0, 0, 0, 0]

    for bit in range(num_bits):
        mask[bit // 8] += 1 << (7 - bit % 8)

    return mask


def split_address(raw_address: str) -> List[int]:
    """
    Split raw address into bytes.

    >>> split_address('91.124.230.205/30')
    [91, 124, 230, 205]
    >>> split_address('192.168.1.15/24')
    [192, 168, 1, 15]
    >>> split_address('192.168.1.255/24')
    [192, 168, 1, 255]
    """
    ip_address = get_ip_from_raw_address(raw_address)

    return list(map(int, ip_address.split('.')))


def join_address(bytes_lst: List[int]) -> str:
    """
    Join bytes into IP address.

    >>> join_address([91, 124, 230, 205])
    '91.124.230.205'
    >>> join_address([192, 168, 1, 15])
    '192.168.1.15'
    >>> join_address([192, 168, 1, 255])
    '192.168.1.255'
    """
    return '.'.join(map(str, bytes_lst))


def invert_address(bytes_lst: List[int]) -> List[int]:
    """
    Invert the given list of bytes.

    >>> invert_address([255, 0, 0, 0])
    [0, 255, 255, 255]
    >>> invert_address([192, 168, 1, 15])
    [63, 87, 254, 240]
    >>> invert_address([192, 168, 1, 255])
    [63, 87, 254, 0]
    """
    inverted = []

    for byte in bytes_lst:
        inverted.append(byte ^ FULL_BYTE)

    return inverted


def get_info(raw_address: str):
    """
    Get info about the given raw address.

    >>> get_info('91.124.230.205/30')
    IP address: 91.124.230.205
    Network Address: 91.124.230.204
    Broadcast Address: 91.124.230.207
    Binary Subnet Mask:	11111111.11111111.11111111.11111100
    First usable host IP: 91.124.230.205
    Penultimate usable host IP: 91.124.230.205
    Number of usable Hosts: 2
    IP class: A
    IP type private: False
    """
    print('IP address:', get_ip_from_raw_address(raw_address))
    print('Network Address:', get_network_address_from_raw_address(raw_address))
    print('Broadcast Address:', get_broadcast_address_from_raw_address(raw_address))
    print('Binary Subnet Mask:', get_binary_mask_from_raw_address(raw_address))
    print('First usable host IP:',
          get_first_usable_ip_address_from_raw_address(raw_address))
    print('Penultimate usable host IP:',
          get_penultimate_usable_ip_address_from_raw_address(raw_address))
    print('Number of usable Hosts:',
          get_number_of_usable_hosts_from_raw_address(raw_address))
    print('IP class:', get_ip_class_from_raw_address(raw_address))
    print('IP type private:', check_private_ip_address_from_raw_address(raw_address))


if __name__ == '__main__':
    import doctest
    doctest.testmod()

    get_info(input())
