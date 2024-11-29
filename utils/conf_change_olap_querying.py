"""
This script modifies ModelarDB's config file to use the right 
1) query engine
2) data source to ingest
3) dimension file
4) sampling interval
5) query interface
"""
import re
import configparser

import conf_change


def main(conf_path, *args):
   """
   main method first must accept the path to ModelarDB config file
   and then the key-values like: dimensions=/path/to/dim.txt
    
   """

   with open(f"{conf_path}" , "r") as f:
       lines = f.read()

   for arg in args:
      k = arg.split("=")[0]
      w = arg.split("=")[1]

      if k.endswith("dimensions"):
         # change dim file location
         lines = re.sub("dimensions\s.+", f"dimensions {w}", lines) 
      elif k.endswith("source"):
         # change sources file location
         lines = re.sub("source\s.+", f"source {w}", lines)
      elif k.endswith("interval"):
         lines = re.sub("sampling_interval\s.+", f"sampling_interval {w}", lines) 
      elif k.endswith("engine"):
         lines = re.sub("engine\s.+", f"engine {w}", lines)
      elif k.endswith("interface"):
         lines = re.sub("interface\s.+", f"interface {w}", lines)
   # add save format type 
   if "modelardb.storage orc" not in lines:
         lines = lines + '\nmodelardb.storage orc:./modelardb'
   # comment out ingestion of correlated time series
   if "#modelardb.correlation auto" not in lines:
      lines = re.sub("modelardb.correlation auto","#modelardb.correlation auto", lines)
      
   with open(f"{conf_path}" , "w") as f:
       f.write(lines)


if __name__ == "__main__":
    # read config file
    config = configparser.ConfigParser()
    config.read("config.cfg")
    conf_change.main(
        config['DEFAULT']['MODELARDB_PATH'] + '/modelardb.conf',
        'engine=' + config['INGESTION']['PROCESSING_ENGINE'],
        'dimensions=' + config['INGESTION']['DIMENSIONS_FILE'],
        'source=' + config['INGESTION']['DATA_PATH'],
        'interval=' + config['INGESTION']['SAMPLING_INTERVAL'],
        'interface=' + config['OLAP_QUERIES']['INTERFACE']
    )