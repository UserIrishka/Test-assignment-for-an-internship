def is_valid_ipv4(ip):
    """Проверка структуры и формата IPv4"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False

    for part in parts:
        if not part.isdigit():
            return False
        if len(part) > 1 and part.startswith('0'):
            return False
        if not (0 <= int(part) <= 255):
            return False
    return True

def is_valid_ipv6(ip):
    """Проверка структуры и формата IPv6"""
    if ip.count('::') > 1 or ':::' in ip:
        return False

    if '::' in ip:
        parts = ip.split('::')
        left = parts[0].split(':') if parts[0] else []
        right = parts[1].split(':') if parts[1] else []

        if '' in left or '' in right:
            return False
        if len(left) + len(right) > 7:
            return False
        all_parts = left + right
    else:
        all_parts = ip.split(':')
        if len(all_parts) != 8:
            return False

    for part in all_parts:
        try:
            val = int(part, 16)
            if not (0 <= val <= 65535):
                return False
        except ValueError:
            return False
    return True

def ipv4_to_bin(ip):
    """Конвертация IPv4 в 32-битную строку"""
    bin_result = ""
    for part in ip.split('.'):
        number = int(part)
        binary_part = bin(number)[2:].zfill(8)
        bin_result += binary_part
    return bin_result

def ipv6_to_bin(ip):
    """Конвертация IPv6 в 128-битную строку с учетом (::)"""
    if '::' in ip:
        parts = ip.split('::')
        left = parts[0].split(':') if parts[0] else []
        right = parts[1].split(':') if parts[1] else []
        missing_zeroes = 8 - (len(left) + len(right))
        full_parts = left + ['0'] * missing_zeroes + right
    else:
        full_parts = ip.split(':')

    bin_result = ""
    for part in full_parts:
        number = int(part, 16)
        binary_part = bin(number)[2:].zfill(16)
        bin_result += binary_part
    return bin_result

def get_min_mask(ip1, ip2):
    """Проверка на валидность и определение версии IP"""
    if is_valid_ipv4(ip1) and is_valid_ipv4(ip2):
        version = 4
        bin1, bin2 = ipv4_to_bin(ip1), ipv4_to_bin(ip2)
        total_bits = 32
    elif is_valid_ipv6(ip1) and is_valid_ipv6(ip2):
        version = 6
        bin1, bin2 = ipv6_to_bin(ip1), ipv6_to_bin(ip2)
        total_bits = 128
    else:
        raise ValueError("Некорректные IP-адреса или попытка сравнить IPv4 с IPv6")
    
    """Поиск длины общего префикса"""
    prefix_length = 0
    for b1, b2 in zip(bin1, bin2):
        if b1 == b2:
            prefix_length += 1
        else:
            break

    """Формирование маски"""
    mask_bin = '1' * prefix_length + '0' * (total_bits - prefix_length)

    if version == 4:
        mask_parts = []
        for i in range(0,32,8):
            octet_bin = mask_bin[i:i + 8]
            octet_int = int(octet_bin, 2)
            mask_parts.append(str(octet_int))
        
        mask_string = '.'.join(mask_parts)

    else:
        mask_parts = []
        for i in range(0,128,16):
            hextet_bin = mask_bin[i:i + 16]
            hextet_int = int(hextet_bin, 2)
            hex_value = hex(hextet_int)
            hex_value = hex_value[2:]            
            hex_value = hex_value.zfill(4)    
            mask_parts.append(hex_value)
        
        mask_string = ':'.join(mask_parts)

    return {
        "version": f"IPv{version}",
        "prefix": f"/{prefix_length}",
        "mask": mask_string

    }

# Проверка валидации
assert is_valid_ipv4("192.168.1.1") == True
assert is_valid_ipv4("192.168.01.1") == False
assert is_valid_ipv6("2001:db8::1") == True
assert is_valid_ipv6("2001::db8::1") == False

print(get_min_mask("192.168.1.10", "192.168.1.20")) # совпадают по границе октета
print(get_min_mask("10.0.0.1", "192.168.1.1")) #не совпадают полностью
print(get_min_mask("192.168.1.10", "192.168.1.10")) #полностью совпадают 
print(get_min_mask("10.10.1.1", "10.10.3.255"))
print(get_min_mask("2001::1", "2001:0:0:0:0:0:0:1")) # проверка для ip6 на развертывания ::
print(get_min_mask("2001:db8:a::", "2001:db8:b::")) # совпадение внутри хекстета


# тесты на ошибки 
try:
    print(get_min_mask("192.168.1.1", "2001:db8::1")) # смешивание видов
except ValueError as e:
    print(f"Поймана ожидаемая ошибка: {e}")

try:
    print(get_min_mask("", "")) # проверка на пустые строки
except ValueError as e:
    print(f"Поймана ожидаемая ошибка: {e}")


