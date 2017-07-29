from lightsaber.log import CloudLog


def test():
    cloud = CloudLog('testd1/testd2', 'log_name')
    cloud.update_spread_sheet(['hoge1', 'hoge2', 'hoge3', 'hoge4'])
    cloud.update_spread_sheet(['hoge11', 'hoge12', 'hoge13', 'hoge14'])
    cloud.update_spread_sheet(['hoge111', 'hoge112', 'hoge113', 'hoge114'])


if __name__ == '__main__':
    test()
