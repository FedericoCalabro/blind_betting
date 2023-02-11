from downloader import PalisenstoDownloader
from supervisor import PalinsestoSupervisor
from reader import PalinsestoPdfReader
from transform import PalinsestoTransformer
from saver import PalinsestoSaver
from speaker import Speaker
from query_master import QueryMaster
from grouper import Grouper
from controller import Controller

supervisor = PalinsestoSupervisor()
downloader = PalisenstoDownloader(supervisor)
reader = PalinsestoPdfReader()
transformer = PalinsestoTransformer(reader)
saver = PalinsestoSaver(transformer)
speaker = Speaker()
query_master = QueryMaster(debug=False)
grouper = Grouper(query_master)
controller = Controller(grouper, speaker)
