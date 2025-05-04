from parser.resp_parser import Parser
#from tokenizer.resp_tokenizer import Tokenizer

def test() -> None:
    first_resp_str: str = "*2\r\n$4\r\nPING\r\n$4\r\nECHO\r\n$5\r\nfoods\r\n"
    parser = Parser(first_resp_str)
    parser.each_token()
    print(parser.get_tokens())
    print()

    second_resp_str: str = "*1\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
    parser = Parser(second_resp_str)
    parser.each_token()
    print(parser.get_tokens())
    print()

    third_resp_str: str = """
    *1\r\n$3\r\nSET\r\n$3\r\nbar\r\n$14\r\nfood truck bar\r\n$2\r\nEX\r\n$2\r\n60\r\n
    """
    parser = Parser(third_resp_str)
    parser.each_token()
    print(parser.get_tokens())
    print()

    fourth_resp_str: str = """
    *1\r\n$6\r\nCLIENT\r\n$7\r\nSETINFO\r\n$8\r\nLIB-NAME\r\n$8\r\nredis-py\r\n
    """
    parser = Parser(fourth_resp_str)
    parser.each_token()
    print(parser.get_tokens())
    print()

    fifth_resp_str: str = """
    *1\r\n$6\r\nCLIENT\r\n$7\r\nSETINFO\r\n$7\r\nLIB-VER\r\n$5\r\n5.0.8\r\n
    """
    parser = Parser(fifth_resp_str)
    parser.each_token()
    print(parser.get_tokens())
    print()

    sixth_resp_str: str = """
    *1\r\n$3\r\nSET\r\n$9\r\n151587081\r\n$9\r\n151587081\r\n
    """
    parser = Parser(sixth_resp_str)
    parser.each_token()
    print(parser.get_tokens())
    print()

    seventh_resp_str: str = """
    *1\r\n$3\r\nSET\r\n$9\r\n151587081\r\n$106\r\nCH,Switzerland,Zurich,Zurich,47.36683,8.54979,de_CH,en_US,Europe/Zurich,+02:00,CEST,de_CH-latin1,qwerty-en\r\n
    """
    parser = Parser(seventh_resp_str)
    parser.each_token()
    print(parser.get_tokens())
    print()

    eighth_resp_str: str = "*1\r\n$4\r\nKEYS\r\n$1\r\n*\r\n"
    parser = Parser(eighth_resp_str)
    parser.each_token()
    print(parser.get_tokens())
    print()

if __name__ == "__main__":
    test()
