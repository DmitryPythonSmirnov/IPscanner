"""
Требования: Python 3.6 и выше.
Никаких дополнительных библиотек не требуется.

Скрипт запрашивает начальный IP-адрес и количество IP-адресов
для проверка на ping, начиная с начального.
Ожидает ответ на 1 ping.
Результат выводится в виде перечисления IP-адресов с результатом проверки,
а также в виде таблицы.
Пример:


209.85.233.125: Узел доступен
209.85.233.126: Узел недоступен
209.85.233.127: Узел доступен
209.85.233.128: Узел доступен
209.85.233.129: Узел доступен
209.85.233.130: Узел недоступен
209.85.233.131: Узел доступен

-------------------------------------
|    Reachable    |   Unreachable   |
-------------------------------------
| 209.85.233.125  | 209.85.233.126  |
| 209.85.233.127  | 209.85.233.130  |
| 209.85.233.128  |                 |
| 209.85.233.129  |                 |
| 209.85.233.131  |                 |
-------------------------------------


Скрипт должен работать на Windows, Linux и Mac OS, так как проверяет тип платформы
и передаёт в команду ping соответствующий ключ для количества пингов:
-n - для Windows
-с - для Linux и Mac OS
"""

import ipaddress
import os
import subprocess
from typing import Dict, Iterator, List, Union


def get_count_flag() -> Union[str, None]:
    """
    Функция возвращает ключ для количества пингов
    в зависимости от ОС (None - если тип ОС неизвестен скрипту):
    -n - для Windows
    -с - для Linux и Mac OS
    """
    count_flag = None
    if os.name == "nt":
        count_flag = "-n"
    elif os.name == "posix":
        count_flag = "-c"

    return count_flag


def is_ipaddr(ipaddr: str) -> bool:
    """
    Проверка, является ли переданный аргумент 'ipaddr'
    IP-адресом или нет
    """
    try:
        ipaddress.ip_address(ipaddr)
        return True
    except ValueError:
        return False


def host_ping(
    ipaddrs_list: Iterator[str], ping_count: str = "1"
) -> Union[Dict[str, List[str]], None]:
    """
    Функция пингует IP-адреса из ipaddrs_list,
    возвращает словарь all_ipaddrs_dict
    со списком доступных IP-адресов (reachable_list)
    и списком недоступных IP-адресов (unreacheable_list)
    """

    # Список доступных адресов в виде строк
    reachable_list: List[str] = []

    # Список недоступных адресов в виде строк
    unreacheable_list: List[str] = []

    all_ipaddrs_dict: Dict[str, List[str]] = {
        "Reachable": reachable_list,
        "Unreachable": unreacheable_list,
    }

    count_flag: Union[str, None] = get_count_flag()
    if count_flag is None:
        print("Неизвестная ОС")
        return None

    ip: str
    for ip in ipaddrs_list:
        if is_ipaddr(ip):
            # Если ip - строка в виде IP-адреса, то преобразуем её
            # в объект IPv4Address или IPv6Address
            host: Union[ipaddress.IPv4Address, ipaddress.IPv6Address] = ipaddress.ip_address(ip)
            host_str: str = str(host)
        else:
            host_str = ip

        # Пингуем и сохраняем результат пинга в res
        # res - это код завершения команды ping, полученный от ОС
        res: int = subprocess.call(
            ["ping", count_flag, ping_count, host_str],
            stdout=subprocess.DEVNULL
        )

        if res == 0:
            print(f"{host_str}: Узел доступен")
            reachable_list.append(host_str)
        else:
            print(f"{host_str}: Узел недоступен")
            unreacheable_list.append(host_str)

    return all_ipaddrs_dict


def get_start_addr() -> Union[
    ipaddress.IPv4Address, ipaddress.IPv6Address, None
]:
    """
    Функция возвращает объект начального IP-адреса или None
    """
    start_ipaddr: str = input("Введите начальный IP-адрес: ")

    while start_ipaddr != "q":
        if not is_ipaddr(start_ipaddr):
            print()
            print("Вы ввели неправильный IP-адрес")
            start_ipaddr = input(
                "Введите начальный IP-адрес или q для выхода: "
            )
        else:
            break

    if start_ipaddr == "q":
        return None
    else:
        return ipaddress.ip_address(start_ipaddr)


def get_num_hosts() -> Union[int, None]:
    """
    Функция возвращает число хостов для проверки или None
    """
    num_hosts: str = input("Введите количество хостов для проверки: ")

    while num_hosts != "q":
        if not num_hosts.isdigit():
            print()
            print("Вы ввели не число")
            num_hosts = input("Введите количество хостов или q для выхода: ")
        else:
            break

    if num_hosts == "q":
        return None
    else:
        return int(num_hosts)


###############################################################################
#                               Main function                                 #
###############################################################################
def host_range_ping() -> Union[Dict[str, List[str]], None]:
    """
    Функция пингует диапазон IP-адресов
    и возвращает словарь со списком доступных
    и недоступных IP-адресов или None
    """
    start_addr: Union[
        ipaddress.IPv4Address, ipaddress.IPv6Address, None
    ] = get_start_addr()
    if start_addr is None:
        print("IP-адрес не был получен")
        print("Выход")
        return None

    num_hosts: Union[int, None] = get_num_hosts()
    if num_hosts is None:
        print("Количество хостов не было получено")
        print("Выход")
        return None

    # Создаём генератор объектов IP-адресов для проверки
    hosts_gen: Iterator[str] = (str(start_addr + i) for i in range(num_hosts))

    # Вызываем функцию проверки доступности
    all_ipaddrs_dict: Union[Dict[str, List[str]], None] = host_ping(hosts_gen)
    return all_ipaddrs_dict


###############################################################################
#                             tab_print function                              #
###############################################################################
def tab_print(all_ipaddrs_dict: Dict[str, List[str]]) -> None:
    """
    Функция распечатывает результат проверки хостов
    в виде таблицы
    """

    REACHABLE: str = "Reachable"
    UNREACHABLE: str = "Unreachable"

    print()  # Для отделения пустой строкой
    print("-------------------------------------")
    print("|    Reachable    |   Unreachable   |")
    print("-------------------------------------")

    # Определеяем, каких IP-адресов больше
    # Если длины списков одинаковые, то max_list останется пустым
    max_list: List[str] = []
    min_num: int
    print_flag: int
    if len(all_ipaddrs_dict[REACHABLE]) < len(all_ipaddrs_dict[UNREACHABLE]):
        min_num = len(all_ipaddrs_dict[REACHABLE])
        max_list = all_ipaddrs_dict[UNREACHABLE]
        print_flag = 2
    elif len(all_ipaddrs_dict[REACHABLE]) >= len(all_ipaddrs_dict[UNREACHABLE]):
        min_num = len(all_ipaddrs_dict[UNREACHABLE])
        max_list = all_ipaddrs_dict[REACHABLE]
        print_flag = 1

    i: int
    for i in range(min_num):
        print(
            f"| {all_ipaddrs_dict[REACHABLE][i].ljust(15)} | {all_ipaddrs_dict[UNREACHABLE][i].ljust(15)} |"
        )

    if max_list:
        for i in range(min_num, len(max_list)):
            if print_flag == 1:
                print(
                    f'| {all_ipaddrs_dict[REACHABLE][i].ljust(15)} | {" " * 15} |'
                )
            elif print_flag == 2:
                print(
                    f'| {" " * 15} | {all_ipaddrs_dict[UNREACHABLE][i].ljust(15)} |'
                )

    print("-------------------------------------")
    print()  # Для отделения пустой строкой


###############################################################################
#                                  Main part                                  #
###############################################################################
if __name__ == "__main__":
    all_ipaddrs_dict: Union[Dict[str, List[str]], None] = host_range_ping()
    if all_ipaddrs_dict is not None:
        tab_print(all_ipaddrs_dict)
    input("Для выхода нажмите любую клавишу...")
