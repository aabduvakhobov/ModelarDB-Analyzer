import re
import sys

# CONF_PATH = sys.argv[1]
# DIM_PATH = sys.argv[2]
# DATA_PATH = sys.argv[3]
# SAMPLING_INTERVAL = int(sys.argv[4])

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
   # add save format type 
   if "modelardb.storage orc" not in lines:
         lines = lines + '\nmodelardb.storage orc:./modelardb'
   # comment out ingestion of correlated time series
   if "#modelardb.correlation auto" not in lines:
      lines = re.sub("modelardb.correlation auto","#modelardb.correlation auto", lines)
      
   with open(f"{conf_path}" , "w") as f:
       f.write(lines)


if __name__ == "__main__": 
   
   # TODO: argparsing dynamic with keyword args
   if len(sys.argv) < 3:
      raise SyntaxError("Insufficient arguments.")
   else:
      main(sys.argv[1], *sys.argv[2:])   
   
        
