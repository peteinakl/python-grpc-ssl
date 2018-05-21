import argparse
import time
from concurrent import futures

import grpc

import namer_pb2
import namer_pb2_grpc

import namer


class Namer(namer_pb2_grpc.NamerServicer):
    def EnglishFullName(self, request, context):
        response = namer_pb2.NameResponse()
        first = request.first_name
        last = request.last_name
        middle = request.middle_name
        prefix = request.prefix
        suffix = request.suffix
        response.full_name = namer.english_full_name(
            first=first, last=last,
            middle=middle, prefix=prefix,
            suffix=suffix)
        print('Peer: {}\nPeerIdentity: {}\nMetadata: {}'.format(
            context.peer(), context.peer_identity_key(),
            context.invocation_metadata()))
        return response


def serve(port=31000):
    private_key = open('../ssl/server-key.pem').read()
    certificate_chain = open('../ssl/server.pem').read()
    credentials = grpc.ssl_server_credentials(
        [(private_key, certificate_chain)]
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    namer_pb2_grpc.add_NamerServicer_to_server(Namer(), server)
    print('Starting server. Listening on port {}...'.format(port))
    server.add_secure_port('[::]:' + str(port), credentials)
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GRPC-based namer server.')
    parser.add_argument(
        '--port', type=int, default=31000,
        help='The server port')
    args = parser.parse_args()
    serve(args.port)
