# coding=utf-8
__author__ = 'chenlei'

import multiprocessing

# The socket to bind
# 绑定的Socket地址
bind = "0.0.0.0:8000"

# The maximum number of pending connections
# 在所有链接都饱和的情况下，等待队列里允许存在的请求数，超过这个数，连接请求会被重置并返回错误
backlog = 2048

# The number of worker processes for handling requests
# 处理请求的worker总数，一般设置为 2-4 ${cup_cores}
workers = multiprocessing.cpu_count() * 2 + 1

# The type of workers to use
# 每个worker工作的方式，我们选用gevent异步协程worker
worker_class = "gevent"

# The number of worker threads for handling requests
# 出国使用同步的worker，开启的线程数，只有在worker_class=sync时有效
threads = multiprocessing.cpu_count() * 4

# The maximum number of simultaneous clients
# 单个worker最大连接数
worker_connections = 1024

# The maximum number of requests a worker will process before restarting
# 每个worker在接收请求达到一定数量后，要重启，以防止内存泄露
max_requests = 10240

# The maximum jitter to add to the max_requests setting
# 为防止所有的worker一块儿重启，会随机一个数字
max_requests_jitter = 60

# Workers silent for more than this many seconds are killed and restarted
# 对于异步worker，如果一个连接时间过长，并且没有数据交互，超过这个时间，会把worker重启
timeout = 30

# Timeout for graceful workers restart
# 在收到重启的信号后，worker最多还能处理多长时间的请求
graceful_timeout = 30

# The number of seconds to wait for requests on a Keep-Alive connection
# 在keepalive连接中接收请求的等待时间
keepalive = 2

# The maximum size of HTTP request line in bytes
# 能接受的最长的http请求，值在0到8190之间，防DDOS攻击参数
limit_request_line = 4094

# Limit the number of HTTP headers fields in a request
# Http请求头中最大的参数个数，防DDOS攻击参数
limit_request_fields = 100

# Limit the allowed size of an HTTP request header field
# Http请求头的最大值，防DDOS攻击参数
limit_request_field_size = 8190

# A base to use with setproctitle for process naming
proc_name = "console"

# A base to use with setproctitle for process naming
default_proc_name = "console"
