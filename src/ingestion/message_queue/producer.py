import pika


connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))

class ProducerQueue:
    def __init__(self,
                host : str,
                queue_name : str):

        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host))
            self.channel = connection.channel()
        except:
            raise ValueError
        self.queue_name = queue_name
        self.channel.queue_declare(queue_name)

    def add_task(self,
                routing_key : str,
                body : str,
                exchange : str = ""):

        if not self.connection.is_open:
            self.connection

        self.channel.basic_publish(
            exchange = exchange,
            routing_key = routing_key,
            body = body
        )
        