import java.io.IOException;
import java.sql.Timestamp;
import java.util.*;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;

import org.apache.iotdb.tsfile.file.metadata.enums.TSDataType;
import org.apache.iotdb.tsfile.write.record.Tablet;
import org.apache.iotdb.tsfile.write.schema.MeasurementSchema;

import org.apache.hadoop.hive.ql.exec.vector.DoubleColumnVector;
import org.apache.hadoop.hive.ql.exec.vector.TimestampColumnVector;
import org.apache.iotdb.session.Session;

import org.apache.orc.OrcFile;
import org.apache.orc.Reader;

@SuppressWarnings({"squid:S106"})
public class Main {
    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            usageAndExit();
        }
        System.out.println("INFO: Start at: " + new Timestamp(System.currentTimeMillis()));
        var inputStringPath = args[0];
        readORCandIngest(inputStringPath);
        System.out.println("INFO: Finished at: " +  new Timestamp(System.currentTimeMillis()));
        }


    private static void usageAndExit() {
        System.out.println(
                "usage: java -jar uberjar input.orc");
        System.exit(0);
    }


    private static void readORCandIngest(String inputStringPath) throws Exception {

        try (Session session = new Session("127.0.0.1", 6667, "root", "root")) {
            session.open();
            // test start
            // create Pipe to the cloud
            session.executeNonQueryStatement("create pipe a2b with sink ('sink'='iotdb-thrift-sink', 'sink.ip'='000.00.00.00', 'sink.port'='6668')");
            // start the Pipe
            session.executeNonQueryStatement("start pipe a2b");
            long allStart = System.nanoTime();
            var reader = createORCReader(inputStringPath);
            // reads all rows and columns
            var rows = reader.rows();
            var batch = reader.getSchema().createRowBatch();

            // construct the tablet's measurements.
            // signals names are not disclosed due to NDA
            String[] signals = {
                    "signal1.."
            };
            List<MeasurementSchema> schemas = contructMeasurements(signals);
            String deviceId = "root.pcd";

            // define Java collection objects to store each column in a batch

            // Start reading a batch and ingest it to the IoTDB in Tablet
            while (rows.nextBatch(batch)) {
                var tv = (TimestampColumnVector) batch.cols[0];
                var acv = (DoubleColumnVector) batch.cols[1];
                var acv60 = (DoubleColumnVector) batch.cols[2];
                var acv600 = (DoubleColumnVector) batch.cols[3];
                var av = (DoubleColumnVector) batch.cols[4];
                var rrvp = (DoubleColumnVector) batch.cols[5];
                var rpv = (DoubleColumnVector) batch.cols[6];
                var pev = (DoubleColumnVector) batch.cols[7];
                var fv = (DoubleColumnVector) batch.cols[8];
                var pulv = (DoubleColumnVector) batch.cols[9];
                var pllv = (DoubleColumnVector) batch.cols[10];
                HashMap<String,  double[]> data = new HashMap<>();
                data.put("s1", pulv.vector);
                data.put("s2", pev.vector);
                data.put("s3", av.vector);
                data.put("s4", acv.vector);
                data.put("s5", acv60.vector);
                data.put("s6", acv600.vector);
                data.put("s7", rpv.vector);
                data.put("s8", rrvp.vector);
                data.put("s9", pllv.vector);
                data.put("s10", fv.vector);

                // create IOTDB Tablet
                Tablet ta = new Tablet(deviceId, schemas, batch.size);
//                System.out.println("Vals in batch:" + batch.size);
                for (int row = 0; row < batch.size; row++) {
                    Timestamp ts = tv.asScratchTimestamp(row);
                    ta.addTimestamp(row, ts.getTime());
                    ta.rowSize++;
                    for (int signal = 0; signal < signals.length; signal++) {
                        ta.addValue(signals[signal], row, (float) data.get(signals[signal])[row]);
                    }
                }
                // now after inserting all data in the batch, insert the tablet
                session.insertAlignedTablet(ta, false);
            }
            rows.close();
            session.executeNonQueryStatement("FLUSH");
            System.out.println("INFO: FLUSH executed at: " + new Timestamp(System.currentTimeMillis()));
            System.out.println(String.format("INFO: Data read and ingestion: %.3f s", ((float) (System.nanoTime() - allStart) / 1000_000_000)) );
        }
    }

        private static Reader createORCReader (String stringPath) throws IOException {
            var path = new Path(stringPath);
            var ro = OrcFile.readerOptions(new Configuration());
            return OrcFile.createReader(path, ro);
        }

        private static List<MeasurementSchema> contructMeasurements (String[] signals) {
            Map<String, TSDataType> measureTSTypeInfos = new HashMap<>();
            for (int signal = 0; signal < signals.length; signal++){
                measureTSTypeInfos.put(signals[signal], TSDataType.FLOAT);
            }
            List<MeasurementSchema> schemas = new ArrayList<>();
            measureTSTypeInfos.forEach((mea, type) -> schemas.add(new MeasurementSchema(mea, type)));
            return schemas;
    }
}
