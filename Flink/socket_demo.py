import sys
import socket
from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import FlatMapFunction

class SocketReader(FlatMapFunction):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def flat_map(self, value):
        print(f"Connecting to {self.host}:{self.port}...", flush=True)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.host, self.port))
            f = s.makefile(encoding='utf-8')
            while True:
                line = f.readline()
                if not line:
                    break
                if line.strip():
                    print(f"Received: {line.strip()}", flush=True)
                    yield line.strip()
        except Exception as e:
            print(f"Socket Error: {e}", flush=True)
        finally:
            s.close()

def socket_demo(host, port):
    # 1. Set up the environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    
    print(f"Listening on {host}:{port}...", flush=True)

    # 2. Create DataStream using a dummy source and a FlatMap to read from socket
    # We use a single element to trigger the FlatMap once
    lines = env.from_collection(["start"]) \
               .flat_map(SocketReader(host, port), output_type=Types.STRING())

    # 3. Transformations
    # Split -> Map((word, 1)) -> KeyBy(word) -> Reduce(sum)
    counts = lines.flat_map(lambda x: x.split(), output_type=Types.STRING()) \
                  .map(lambda i: (i, 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
                  .key_by(lambda i: i[0]) \
                  .reduce(lambda i, j: (i[0], i[1] + j[1]))

    # 4. Sink (Print to stdout)
    counts.print()

    # 5. Execute
    print("Submitting job...", flush=True)
    env.execute("Socket Window WordCount")
    print("Job finished.", flush=True)

if __name__ == "__main__":
    # Default to localhost:9000 if no args provided
    host = "localhost"
    port = 9000
    if len(sys.argv) >= 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    
    socket_demo(host, port)
