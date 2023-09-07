if __name__ == '__main__':
    string = "16A07701"
    byte_data = bytes.fromhex(string)
    #获取第一个字节
    first_byte = byte_data[0]
    if (first_byte & 0x01)  == 0x00:
        #心率小于255，获取后面一个字节
        heartRate = int(byte_data[1])
        print(heartRate)
    for by in byte_data:
        print(by)