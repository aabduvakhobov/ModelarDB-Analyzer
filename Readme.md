# ModelarDB Analyzer for multi-model Error-Bounded Lossy and Lossless Compression (EBLLC)
Analyzer is a python program created for implementing and analyzing the performance of EBLLC on ModelarDB TSMS. We use [ModelarDB-JVM](https://github.com/modelardata/modelardb) for this purpose.

To run the program:
1. Clone [ModelarDB-JVM](https://github.com/modelardata/modelardb) repository and apply the [git patch file](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/ModelarDB-Extended-Logging.patch) in the root of this repository.
2. Set the desired configurations in the [config.cfg](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/config.cfg)   
3. Run [main.py](https://github.com/aabduvakhobov/ModelarDB-Analyzer/blob/main/main.py)

There are handful of useful shell scripts in the [Utilities]() folder

To run ModelarDB in the edge-to-cloud scenario: 
  1. Configure the same data source, dimensions file and error bounds in conf files for both instances of ModelarDB (edge and cloud)
  2. Make sure that cloud's conf file is on a server transfer mode\* like: *modelardb.transfer server*
  3. Make sure that edge's conf file has cloud's IP address for transfer: *modelardb.transfer xxx.xx.xx.xx*
  4. Start the cloud and the edge.

\* Make sure that hostname ip resolves to what is shown in the conf file. Otherwise it needs to be changed from */etc/hosts* 
