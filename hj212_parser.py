class HJ212Parser:
    def __init__(self):
        pass

    def is_valid_message(self, message: str) -> bool:
        """
        检查HJ212报文整体格式合法性
        格式：## + 4位长度 + 数据段 + 4位CRC + \r\n
        """
        # 必须以##开头，以\r\n结尾
        if not message.startswith("##") or not message.endswith("\r\n"):
            return False
        # 剥离头部## 和尾部\r\n
        body = message[2:-2]
        if len(body) < 8:
            return False
        # 前4字符为报文长度，必须是数字
        len_str = body[0:4]
        if not len_str.isdigit():
            return False
        msg_len = int(len_str)
        # 数据段 = body[4:-4]，后面4位是CRC
        data_segment = body[4:-4]
        crc_str = body[-4:]
        if not crc_str.isalnum():
            return False
        # 校验长度是否匹配
        if len(data_segment) != msg_len:
            return False
        return True

    def validate_crc(self, message: str) -> bool:
        """
        ANSI CRC16校验，初始0xFFFF，多项式0xA001
        计算数据段CRC，和报文中携带的CRC对比
        """
        if not self.is_valid_message(message):
            return False
        body = message[2:-2]
        data_segment = body[4:-4]
        received_crc_hex = body[-4:]
        # 计算数据段的crc16
        calc_crc = self._crc16_ansi(data_segment.encode('gbk'))
        received_crc = int(received_crc_hex, 16)
        return calc_crc == received_crc

    def _crc16_ansi(self, data: bytes) -> int:
        """内部：ANSI CRC16 算法，初始0xFFFF，多项式0xA001"""
        crc = 0xFFFF
        poly = 0xA001
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ poly
                else:
                    crc >>= 1
        return crc & 0xFFFF

    def parse_data_segment(self, message: str) -> dict:
        """
        解析数据段，返回全部键值对字典
        解析如：QN=20220223160000;ST=32;CN=2011;PW=123456;MN=010000A8900016F00035;CP=&&DataTime=20220223155959;w0101=10.00&&
        """
        if not self.is_valid_message(message):
            raise ValueError("报文格式非法")
        body = message[2:-2]
        data_segment = body[4:-4]
        result = {}
        parts = data_segment.split(';')
        for part in parts:
            if '=' in part:
                k, v = part.split('=', 1)
                result[k.strip()] = v.strip()
        return result

    def extract_monitoring_data(self, message: str) -> dict:
        """
        从CP字段提取监测因子，例如 w0101=10.00;w0102=20.1
        返回 {因子编码:数值}
        """
        data_dict = self.parse_data_segment(message)
        cp_str = data_dict.get("CP", "")
        # CP格式 &&xxx&&，去掉前后&&
        cp_content = cp_str.strip("&")
        monitor_data = {}
        if not cp_content:
            return monitor_data
        items = cp_content.split(';')
        for item in items:
            if '=' in item:
                factor_code, val = item.split('=',1)
                monitor_data[factor_code.strip()] = val.strip()
        return monitor_data


# ============ 测试示例 ============
if __name__ == "__main__":
    # 示例HJ212报文（仅供测试）
    test_msg = "##0207QN=20220223160000;ST=32;CN=2011;PW=123456;MN=010000A8900016F00035;CP=&&DataTime=20220223155959;w0101=10.00&&B536\r\n"
    parser = HJ212Parser()

    print("报文格式是否合法：", parser.is_valid_message(test_msg))
    print("CRC校验是否通过：", parser.validate_crc(test_msg))
    print("\n数据段全部字段：")
    print(parser.parse_data_segment(test_msg))
    print("\n提取监测因子数据：")
    print(parser.extract_monitoring_data(test_msg))
