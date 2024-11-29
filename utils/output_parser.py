import os
import re
import json
from pathlib import Path
import time

import configparser


config = configparser.ConfigParser()
config.read("config.cfg")
    
class OutputParser:
    """
    docstring:
    """

    def __init__(
            self,
            data_path,
            output_path,
            error_bound
    ):
        self.data_path = data_path
        self.output_path = output_path
        self.error_bound = error_bound

    # private methods
    def __estimate_dir(self):
        # assign size
        size = 0
        # get size
        for path, dirs, files in os.walk(self.data_path):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
        return size

    def __file_size_estimate(self, error):
        # reads a file
        # fetches the needed records: 1st and last elements of the list
        # pattern matching for suitable types
        # sums them up at the end
        with open(self.output_path + f"/verifier-{error}-0.0", "r") as f:
            # fetch only the part after EVALUATION RESULT
            line = f.read().split("EVALUATION RESULT")[1]
            # gets everything in the parenthesis after the file name in a list of records
            # e.g: PowerUpperLimit.orc: [(479908819,0.045610520159400245,0.0999999911940832,2.34729532E8,1.0706136051292585E7,Float)]
            records = re.findall(f":\s+\[\((.+)\)\]", line)
            byte_sum = 0
            for r in records:
                # list contains several strings of metrics for each TS file and error bound, so they're split
                num_rows = r.split(",")
                # in accordance with data type they're calculated
                # must also include the size of each timestamp: 32bit (epoch time in seconds) or 64 bit (milliseconds)
                # as you are ingesting multivariate ts, you should consider ts col only once
                if byte_sum == 0:
                    byte_sum += int(num_rows[0]) * (4 + 8)
                else:
                    byte_sum += int(num_rows[0]) * 4
                # pattern matching method for different variables types and their vals
        return byte_sum

    # public methods
    def parse_file_size_ver(self):
        output_list = []
        for error in self.error_bound.split(" "):
            # actual file size comes in Bytes
            actual_size_before_compression = self.__estimate_dir()
            theoretical_file_size = self.__file_size_estimate(error)
            # output_list["original_data_size"] = file_size
            with open(self.output_path + f"/output-{error}-0.0", "r") as f:
                lines = f.read().rstrip()
                # fetch compressed size, it comes in KB so converting to Bytes... later on
                compressed = int(re.findall("final_size=[0-9]*", lines)[0].split("=")[1]) * 1024
                # now expected size, already comes in bytes
                models_size = int(re.findall("Models Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2])
                metadata_size = int(re.findall("Metadata Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2])
                gaps_size = int(re.findall("Gaps Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2])
                total_expected_size = int(re.findall("Total Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2])
            output_list.append((error, theoretical_file_size, actual_size_before_compression, compressed, models_size, metadata_size, gaps_size, total_expected_size))
        return output_list

    def parse_segment_size(self):
        output_list = []
        # used as a primary key in the table
        segments = {}
        datapoints = {}
        # iterate over error bounds set
        for error in self.error_bound.split(" "):            
            # open the file
            with open(self.output_path + f"/output-{error}-0.0", "r") as f:
                lines = f.read().rstrip()
                # declare every param in a variable
                # find the data source name
                signal = re.findall("Sources:\s+{(.+)}", lines)
                # get the whole line and fetch the number out of it, also there might not be anything
                pmc_segments = re.findall("PMC_MeanModelType \| Count:\s+([0-9]+)", lines)
                swing_segments = re.findall("SwingFilterModelType \| Count:\s+([0-9]+)", lines)
                gorilla_segments = re.findall("FacebookGorillaModelType \| Count:\s+([0-9]+)", lines)
                pmc_data_points = re.findall("PMC_MeanModelType \| DataPoint:\s+([0-9]+)", lines)
                swing_data_points = re.findall("SwingFilterModelType \| DataPoint:\s+([0-9]+)", lines)
                gorilla_data_points = re.findall("FacebookGorillaModelType \| DataPoint:\s+([0-9]+)", lines)

                segments["pmc"] = pmc_segments
                datapoints["pmc"] = pmc_data_points
                segments["swing"] = swing_segments
                datapoints["swing"] = swing_data_points
                segments["gorilla"] = gorilla_segments
                datapoints["gorilla"] = gorilla_data_points
                
            with open(self.output_path + f"/verifier-{error}-0.0", "r") as f:
                # fetch only the part after EVALUATION RESULT
                veri_line = f.read().split("EVALUATION RESULT:")[1].split("[success]")[0].strip()
                metrics = {}
                # single row would look like:  id, ts, error_bound, model_type, segment
                for i, v in enumerate(signal):
                    # fetch everything after the file name
                    metrics[v] = re.findall(f"{v}:\s+\[\((.+)\)\]", veri_line)[0].split(",")
                    for model in zip(["pmc", "swing", "gorilla"], [7,8,9]) :
                        output_list.append(
                            # now create collection of tuples in accordance with data tables
                            (   
                                v, error, model[0] , datapoints[model[0]][i], segments[model[0]][i], metrics[v][model[1]]
                            )
                        )

        # print(output_list)
        return output_list

    # parses verifier... logs for error table
    def parse_errors(self):
        output_list = []
        # iterate over error bounds set
        for error in self.error_bound.split(" "):
            # open the file
            with open(self.output_path + f"/verifier-{error}-0.0", "r") as f:
                # fetch only the part after EVALUATION RESULT
                line = f.read().split("EVALUATION RESULT:")[1].split("[success]")[0].strip()
                # print(line)
                # gets all ts file names in a list of records
                ts = re.findall("(.+):", line)
                ts = [i for i in ts if i != []]
                metrics = {}
                # parse through the ts names
                for ts_1 in ts:
                    # fetch everything after the file name
                    metrics[ts_1] = re.findall(f"{ts_1}:\s+\[\((.+)\)\]", line)[0].split(",")
                    # now create collection of tuples in accordance with data tables
                    # the structure of a single row: (id, ts, error_bound, avg_error, max_error, diff_cnt, cnt, mae)
                    # order of metrics in verifier.. log: (generalCount, averageError, maxError, differenceCount, differenceSum, dataType, averageErrorWithZero) + (seg_median1, seg_median2, seg_median3)
                    output_list.append(
                        (ts_1, error, metrics[ts_1][1], metrics[ts_1][2], metrics[ts_1][3], metrics[ts_1][0], metrics[ts_1][6])
                    )
        return output_list
    
        # maybe two separate files would be parsed separately
    def parse_file_size_hor(self):
        # output_list = [self.__estimate_dir()]
        # output_dict = {"original_file_size": self.__estimate_dir()}
        output_dict = {}
        for error in self.error_bound.split(" "):
            file_size = self.__file_size_estimate(error)
            output_dict["original_data_size"] = file_size
            with open(self.output_path + f"/output-{error}-0.0", "r") as f:
                lines = f.read().rstrip()
                # fetch compressed size
                compressed = int(re.findall("final_size=[0-9]*", lines)[0].split("=")[1])
                # now expected size
                expected = int(re.findall("Total Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2]) / 1000

                output_dict[f"compressed_size_{error}"] = int(compressed) * 1024
                output_dict[f"expected_size_{error}"] = int(expected) * 1024
        return output_dict
    
    
    def parse_actual_error_histogram(self):
        output_list = []
        for error in self.error_bound.split(" "):
            with open(self.output_path + f"/verifier-{error}-0.0", "r") as f:
                veri_line = f.read().split("EVALUATION RESULT:")[0].split("Dataset error histogram: ")[1]
            # parse the list
            hist_tuple = eval(veri_line)
            for t in hist_tuple:
                output_list.append(
                    (error, t[0], t[1]) 
                    )
        return output_list
            # hist_tuple.map(lambda x: output_list.append(x))
            
            

class SegmentAnalyzer:
    """Class to read the compressed time series and retrieve badly compressed segments
    """
    def __init__(
        self, 
        ingested_path, 
        error_bounds):
        self.ingested_path = ingested_path
        self.error_bounds = error_bounds


    def run(self):
        from pyspark.sql import SparkSession
        """main function that iterates through error_bounds and time_series to generate the list of tuples (TS, Error, Data)
        """
        spark = SparkSession.builder.appName("SegmentReadApp").master("local[*]").getOrCreate()
        final_output = []
        for error in [float(i) for i in self.error_bounds.split(" ")]:
            retries = 0
            while retries < 5:
                try:
                    print(f"RUN: Error: {error}")
                    (models, time_series, segment) = self.__read_mdb(spark, error)
                except Exception as e:
                    print(f"Raised an exception: {e}") 
                    time.sleep(30)
                    retries += 1
                else:
                    print(f"Segments-{error} DF was read!")
                    break
            # get time_series list from time_series\
            ts = time_series.toPandas().iloc[:, [0,-1]].values
            # iterate over segments to return list of badly compressed data points if they exist
            print(f"RUN: error: {error}, TS: {ts}")
            output = self.__analyze(segment, ts, error)
            final_output += output
        return final_output
    
    
    def __read_mdb(self, spark, error):
        # to read modelardb dataframe in ORC or Parquet depending on type 
        # now we have to read folders using passed error bound
        file_format = self.__get_storage()
   
        # iterate over root directory to get the right sub dir
        dir = [i for i in os.listdir(self.ingested_path) if i.startswith("modelardb") and i.__contains__("-" + str(error) + "-")][0]
        # define full path
        path = self.ingested_path + "/" + dir
        # read data based on file format
        print(f"READ: reading from: {path}")
        if file_format == "orc":   
            segment = spark.read.orc(path + "/segment/*")
            models = spark.read.orc(path + "/model_type.orc")
            time_series = spark.read.orc(path + "/time_series.orc")
        else:
            segment = spark.read.parquet(path +  "/segment/*")
            models = spark.read.parquet(path + "/model_type.parquet")
            time_series = spark.read.parquet(path + "/time_series.parquet")
    
        return (models, time_series, segment)
    
    
    def __analyze(self, segments, ts, error):
        final_output = []
        # ts_id[0]: tid, ts_id[1]: ts_name
        for ts_id in ts:
            print(f"Analyze: Reading: {ts_id[1]}, Error: {error}")
            df = segments.where(segments.gid == ts_id[0])
            matches = self.__find_consecutive_indexes(df)
            if matches != {}:
                final_output.append((ts_id[0], ts_id[1], error, json.dumps(matches)))
            else:
                print("Nothing was discovered") #TODO: handle this properly
        return final_output
    
    
    # where are the indexes/timestamps?
    # k: [i1, i2, i3, i4, i5 .... i_n]
    def __find_consecutive_indexes(self, spark_df):
        # models = df.mtid.to_list()
        models = spark_df.select("mtid").collect()
        length = len(models)
        counter = 0
        occurences = {}
        
        for i, val in enumerate(models):
            v = int(val[0])
            # if model_id == 4
            if v == int(config['MODEL_TYPES']['GORILLA_ID']) and i+1 < length:
                if v == models[i+1][0]:
                    counter += 1
                    
                else:
                    # if the key exists
                    if occurences.get(f"{counter+1}") is not None:
                        # storing only the fist index for sequence of counter
                        occurences[f"{counter+1}"].append(i-counter)
                    else:
                        # storing only the fist index for sequence of counter
                        occurences[f"{counter+1}"] = [i-counter]
                    # flush the counter                
                    counter = 0
        
        try:
            del occurences["1"]
        except Exception:
            pass
        return occurences


    def __get_storage(self):
        with open(f"{Path.home()}/.modelardb.conf") as f:
            lines = f.readlines()
            line = [line for line in lines if line.__contains__("modelardb.storage") and not line.__contains__("#")][0]
            file_format = "orc" if line.__contains__("orc") else "parquet"
        return file_format
     
    
    