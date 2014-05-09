import unittest
import SimpleHTTPServer
import SocketServer
import threading
 
import hlslocust.hls as hls

# allow sockets to be reused when we rerun tests
SocketServer.TCPServer.allow_reuse_address = True

class TddCasting(unittest.TestCase):
    def test_castInt(self):
        self.assertEqual(hls.myCast('1'),1)
        self.assertEqual(hls.myCast('-1'),-1)

    def test_castFloat(self):
        self.assertEqual(hls.myCast('1.5'),1.5)
        self.assertEqual(hls.myCast('1.0'),1.0)
        self.assertEqual(hls.myCast('-1.0'),-1.0)

    def test_castBool(self):
        self.assertEqual(hls.myCast('NO'),False)
        self.assertEqual(hls.myCast('No'),False)
        self.assertEqual(hls.myCast('no'),False)
        self.assertEqual(hls.myCast('YES'),True)
        self.assertEqual(hls.myCast('Yes'),True)
        self.assertEqual(hls.myCast('yes'),True)

    def test_castList(self):
        self.assertEqual(hls.myCast('No,10,100.0'),[False,10,100.0])

    def test_castDict(self):
        self.assertEqual(hls.myCast('PROGRAM-ID=1127167744,BANDWIDTH=1000000'),
                         {'program_id':1127167744,'bandwidth':1000000})

class TddMasterPlaylist(unittest.TestCase):
    def setUp(self):
        self.hls_player = hls.Player()
        with open('example/NTV-Public-IPS.m3u8') as f:
            self.hls_player.parse(f.read())

    def test_playlists(self):
        playlists = [x.name for x in self.hls_player.playlists]
        self.assertEqual(playlists,
            ['public_1000.m3u8',
             'public_400.m3u8',
             'public_200.m3u8'])

    def test_playlist_bandwidths(self):
        bandwidths = [x.bandwidth for x in self.hls_player.playlists]
        self.assertEqual(bandwidths, [1000000, 400000, 200000])

    def test_playlist_id(self):
        program_ids = [x.program_id for x in self.hls_player.playlists]
        self.assertEqual(program_ids, [1127167744, 1127167744, 1127167744])

    def test_duplicate_playlists(self):
        with open('example/NTV-Public-IPS.m3u8') as f:
            self.hls_player.parse(f.read())
        self.assertEqual(len(self.hls_player.playlists),3)

    def test_playlists_are_remembered(self):
        with open('example/public_200.m3u8') as f:
            self.hls_player.parse(f.read())
        self.assertEqual(len(self.hls_player.playlists),3)


class TddMediaPlaylist(unittest.TestCase):
    def setUp(self):
        self.hls_player = hls.Player()
        with open('example/public_200.m3u8') as f:
            self.hls_player.parse(f.read())

    def test_manifest_queue(self):
        filenames = [x.name for x in self.hls_player.queue]
        self.assertEqual(filenames,
                ['public_200/Num32458.ts',
                 'public_200/Num32459.ts',
                 'public_200/Num32460.ts',
                 'public_200/Num32461.ts',
                 'public_200/Num32462.ts',
                 'public_200/Num32463.ts',
                 'public_200/Num32464.ts',
                 'public_200/Num32465.ts'])

    def test_manifest_durations(self):
        durations = [x.duration for x in self.hls_player.queue]
        self.assertEqual(durations, [3]*8)

    def test_attributes(self):
        self.assertEqual(self.hls_player.media_sequence, 32458)
        self.assertEqual(self.hls_player.allow_cache, False)
        self.assertEqual(self.hls_player.version, 2)

    def test_duplicate_fragments(self):
        with open('example/public_200.m3u8') as f:
            self.hls_player.parse(f.read())
        self.assertEqual(len(self.hls_player.queue),8)

class TddPlay(unittest.TestCase):
    def setUp(self):
        self.hls_player = hls.Player()
        self.server = WebServer()
        self.server.start()

    def tearDown(self):
        self.server.stop()

    def test_play(self):
        playtime = self.hls_player.play('http://localhost:8000/example/NTV-Public-IPS.m3u8')
        self.assertEqual(playtime,24.0)
       

class WebServer(threading.Thread):
    def __init__(self):
        PORT = 8000
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        self.httpd = SocketServer.TCPServer(("", PORT), Handler)
        threading.Thread.__init__(self)

    def run(self):
        self.httpd.serve_forever()

    def stop(self):
        self.httpd.shutdown()

if __name__ == '__main__':
    unittest.main()
   