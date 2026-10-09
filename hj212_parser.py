class HJ212Parser:
    def __init__(self):
        pass

    def _crc16_hj212(self, data: bytes) -> int:
        crc_reg = 0xFFFF
        poly = 0xA001
        for b in data:
            crc_reg ^= b
            for _ in range(8):
                if crc_reg & 0x0001:
                    crc_reg = (crc_reg >> 1) ^ poly
                else:
                    crc_reg = crc_reg >> 1
        return crc_reg

    def is_valid(self, msg: str) -> bool:
        if not msg.startswith("##"):
            return False
        if not msg.endswith("\r\n"):
            return False
        body = msg[2:-2]
        if len(body) < 8:
            return False
        len_text = body[0:4]
        if not len_text.isdigit():
            return False
        expect_len = int(len_text)
        data_area = body[4:-4]
        if len(data_area) != expect_len:
            return False
        return True

    def crc_check(self, msg: str) -> bool:
        if not self.is_valid(msg):
            return False
        body = msg[2:-2]
        data_area = body[4:-4]
        crc_recv = int(body[-4:], 16)
        crc_calc = self._crc16_hj212(data_area.encode("ascii"))
        return crc_calc == crc_recv

    def parse(self, msg: str) -> dict:
        if not self.is_valid(msg):
            raise ValueError("报文格式非法")
        body = msg[2:-2]
        data_area = body[4:-4]
        result = {}
        parts = data_area.split(";")
        for p in parts:
            if "=" in p:
                k, v = p.split("=", 1)
                result[k] = v
        return result


if __name__ == "__main__":
    test_message = "##0101QN=20160801085857223;ST=32;CN=1062;PW=100000;MN=010000A8900016F000169DC0;Flag=5;CP=&&RtdInterval=30&&0759\r\n"
    parser = HJ212Parser()

    print("报文格式是否合法：", parser.is_valid(test_message))
    body = test_message[2:-2]
    data_area = body[4:-4]
    print("数据段：", repr(data_area))
    print("数据段长度：", len(data_area))
    crc_calc = parser._crc16_hj212(data_area.encode("ascii"))
    print("程序算出CRC(16进制大写)：", f"{crc_calc:04X}")
    print("报文自带CRC：", body[-4:])
    print("CRC校验是否通过：", parser.crc_check(test_message))
    print("解析结果：")
    print(parser.parse(test_message))
