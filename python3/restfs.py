import json
import sys
import os
import asyncio

def write_header(writer, status_code=200, content_type='text/html'):
    writer.write('HTTP/1.0 {} NA\r\n'.format(status_code).encode('ascii'))
    writer.write('Content-Type: {}\r\n'.format(content_type).encode('ascii'))
    writer.write(b'Connection: close\r\n')
    writer.write(b'\r\n')


async def write_file_to_writer(filename, writer):
    with open(filename, 'rb') as f:
        while True:
            data = f.read(512)
            if not data:
                break
            writer.write(data)
            await writer.drain()

class Server(object):

    def __init__(self, root):
        self.root = root

    async def read_header(self, reader):
        x = await reader.readline()
        header = {}
        while x != b'\r\n':
            val = x.decode('ascii')
            pos = val.find(':')
            key = val[:pos].strip()  # what is before : 
            value = val[pos+1:].strip() # what is after :
            header[key] = value
            x = await reader.readline()
        return header

    async def get_file(self, path, writer):
        if not os.path.exists(path):
            write_header(writer, status_code=404)
            await writer.drain()
            writer.close()
            return
        if os.path.isdir(path):
            result = os.listdir(result) 
            writer.write(json.dumps({'result': result}).encode('utf8'))
            await writer.drain() 
            writer.close()
            return
        write_header(writer, status_code=404)
        await writer.drain()
        await write_file_to_writer(path, writer)
        return

    async def create_file(self, path, header, reader, writer):
        content = ''
        if 'Content-Length' in header:
            content_len = int(header['Content-Length'])
            content = await reader.read(content_len)
        with open(path, 'bw') as write_file:
            write_file.write(content)
            write_file.flush()
        write_header(writer)
        writer.write(b'{"status": "success"}')
        writer.drain()


    async def handle_request(self, reader, writer):
        x = await reader.readline() # GET /... version
        verb, path, version = x.decode('ascii').split()
        path = path[1:]
        header = await self.read_header(reader)
        print(header)
        realpath = os.path.join(self.root, path)
        if verb == 'GET':
            await self.get_file(realpath, writer)
        if verb == 'PUT':
            await self.create_file(realpath, header, reader, writer)
        writer.drain()
        writer.close()




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    server = Server(root)
    loop.create_task(asyncio.start_server(server.handle_request, port=8000))
    print('serving directory {} on port {}'.format(root, port))
    loop.run_forever()

