import os
import re





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
        def object_size_estimate(obj):
            if obj == "Short":
                return 2
            elif obj == "Int" or obj == "Float":
                return 4
            elif obj == "Double" or obj == "Long" or obj == "BigInt":
                return 8
            else:
                raise TypeError("Unknown type identified")
        with open(self.output_path + f"verifier-{error}-0.0", "r") as f:
            # fetch only the part after EVALUATION RESULT
            line = f.read().split("EVALUATION RESULT")[1]
            # gets everything in the parenthesis after the file name in a list of records
            records = re.findall(f":\s+\[\((.+)\)\]", line)
            byte_sum = 0
            for r in records:
                # list contains several strings of metrics for each TS file and error bound, so they're split
                record = r.split(",")
                # in accordance with data type they're calculated
                # must also include the size of each timestamp: 32bit or 64 bit
                byte_sum += int(record[0]) * object_size_estimate(record[-1]) * 8
                # pattern matching method for different variables types and their vals
        return byte_sum

    # public methods
    # maybe two separate files would be parsed separately
    def parse_file_size_hor(self):
        # output_list = [self.__estimate_dir()]
        # output_dict = {"original_file_size": self.__estimate_dir()}
        output_dict = {}
        for error in self.error_bound.split(" "):
            file_size = self.__file_size_estimate(error)
            output_dict["original_data_size"] = file_size
            with open(self.output_path + f"output-{error}-0.0", "r") as f:
                lines = f.read().rstrip()
                # fetch compressed size
                compressed = int(re.findall("final_size=[0-9]*", lines)[0].split("=")[1])
                # now expected size
                expected = int(re.findall("Total Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2]) / 1000

                output_dict[f"compressed_size_{error}"] = int(compressed) * 1024
                output_dict[f"expected_size_{error}"] = int(expected) * 1024
        return output_dict

    def parse_file_size_ver(self):
        output_list = []
        counter = 0
        for error in self.error_bound.split(" "):
            file_size = self.__file_size_estimate(error)
            # output_list["original_data_size"] = file_size
            with open(self.output_path + f"output-{error}-0.0", "r") as f:
                lines = f.read().rstrip()
                # fetch compressed size, it comes in KB so converting to Bytes... later on
                compressed = int(re.findall("final_size=[0-9]*", lines)[0].split("=")[1]) * 1024
                # now expected size, already comes in bytes
                models_size = int(re.findall("Models Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2])
                metadata_size = int(re.findall("Metadata Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2])
                gaps_size = int(re.findall("Gaps Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2])
                total_expected_size = int(re.findall("Total Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2])
            output_list.append((counter, error, file_size, compressed, models_size, metadata_size, gaps_size, total_expected_size))
            counter += 1
        return output_list

    def parse_segment_size(self):
        output_list = []
        # used as a primary key in the table
        counter = 0
        segments = {}
        datapoints = {}
        # iterate over error bounds set
        for error in self.error_bound.split(" "):
            # open the file
            with open(self.output_path + f"output-{error}-0.0", "r") as f:
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

                # single row would look like:  id, ts, error_bound, model_type, segment
                for i in range(len(signal)):
                    for model in ["pmc", "swing", "gorilla"]:
                        output_list.append(
                            # now create collection of tuples in accordance with data tables
                            (
                                counter, signal[i], error, model, datapoints[model][i], segments[model][i]
                            )
                        )
                        counter += 1

        # print(output_list)
        return output_list

    # parses verifier... logs for error table
    def parse_errors(self):
        output_list = []
        # used as a primary key in the table
        counter = 0
        # iterate over error bounds set
        for error in self.error_bound.split(" "):
            # open the file
            with open(self.output_path + f"verifier-{error}-0.0", "r") as f:
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
                    # the structure of a single row: (id, ts, error_bound, avg_error, max_error, diff_cnt, cnt)
                    output_list.append(
                        (counter, ts_1, error, metrics[ts_1][1], metrics[ts_1][2], metrics[ts_1][3], metrics[ts_1][0])
                    )
                    counter += 1
        return output_list
