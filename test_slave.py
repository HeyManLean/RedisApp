from redis import Redis


main_db = Redis(host='localhost', port=6379)
slave_db1 = Redis(host='localhost', port=6377)
slave_db2 = Redis(host='localhost', port=6378)


main_db.set('aa', 'ok啦!!!')
print('slave_db1', slave_db1.get('aa'))
print('slave_db2', slave_db2.get('aa'))
