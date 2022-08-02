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

    def __estimate_dir(self):
        # assign size
        size = 0
        # get size
        for path, dirs, files in os.walk(self.data_path):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
        return size

    # maybe two separate files would be parsed separately
    def parse_file_size(self):
        # output_list = [self.__estimate_dir()]
        output_dict = {"original_size": self.__estimate_dir()}
        # output_dict["original_size"]
        for error in self.error_bound.split(" "):
            with open(self.output_path + f"/output-{error}-0.0", "r") as f:
                lines = f.read().rstrip()
                # fetch compressed size
                compressed = int(re.findall("final_size=[0-9]*", lines)[0].split("=")[1])
                # now expected size
                expected = int(re.findall("Total Size:\s+[0-9]*\s+[A-Za-z]*", lines)[0].split(" ")[-2]) / 1000

                output_dict[f"compressed_size_{error}"] = compressed
                output_dict[f"expected_size_{error}"] = expected
        # print(output_dict)

        return output_dict

    def parse_segment_size(self):
        output_list = []
        counter = 0
        for error in self.error_bound.split(" "):
            with open(self.output_path + f"/output-{error}-0.0", "r") as f:
                lines = f.read().rstrip()
                # declare every param in a variable
                # cleaned = [re.search("{(.*)}", s).group(1) for s in re.findall("Sources:\s+{.+}", lines)]
                signal = re.findall("Sources:\s+{(.+)}", lines)
                pmc_segments = re.findall("PMC_MeanModelType \| Count:\s+([0-9]+)", lines)
                swing_segments = re.findall("SwingFilterModelType \| Count:\s+([0-9]+)", lines)
                gorilla_segments = re.findall("FacebookGorillaModelType \| Count:\s+([0-9]+)", lines)
                pmc_data_points = re.findall("PMC_MeanModelType \| DataPoint:\s+([0-9]+)", lines)
                swing_data_points = re.findall("SwingFilterModelType \| DataPoint:\s+([0-9]+)", lines)
                gorilla_data_points = re.findall("FacebookGorillaModelType \| DataPoint:\s+([0-9]+)", lines)

                collection = (signal, pmc_segments, swing_segments, gorilla_segments, pmc_data_points,
                              swing_data_points, gorilla_data_points)
                for i in collection:
                    if i == []:
                        i.extend(["0", "0", "0", "0", "0", "0", "0", "0", "0"])

                    # print(f"Error bound: {error}: length: ", len(i))
                # print("segment contents: ", swing_segments)

                # now create insert friendly list of tuples
                for i in range(len(signal)):
                    output_list.append((counter+i, signal[i], error, pmc_data_points[i], swing_data_points[i], gorilla_data_points[i],
                                        pmc_segments[i], swing_segments[i], gorilla_segments[i]))
                counter += i+1
        # print(output_list)
        return output_list

