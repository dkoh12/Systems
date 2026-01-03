from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment

def simple_demo():
    # 1. Set up the execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    print("Executing Flink Job: WordCount from static collection...")

    # 2. Define the source (Static list of strings)
    source_data = [
        "Apache Flink is fast",
        "Flink processes streams",
        "Streams are cool",
        "Apache Flink is powerful"
    ]
    ds = env.from_collection(source_data)

    # 3. Define the transformations
    # Split lines into words -> Map to (word, 1) -> Group by word -> Sum counts
    ds = ds.flat_map(lambda line: line.lower().split(), output_type=Types.STRING()) \
           .map(lambda word: (word, 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
           .key_by(lambda i: i[0]) \
           .reduce(lambda i, j: (i[0], i[1] + j[1]))

    # 4. Define the sink (Print to console)
    ds.print()

    # 5. Execute the job
    env.execute("Simple WordCount")

if __name__ == '__main__':
    simple_demo()
