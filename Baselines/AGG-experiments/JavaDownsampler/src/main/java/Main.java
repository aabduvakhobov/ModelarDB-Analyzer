import java.io.IOException;
import java.sql.Timestamp;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.hive.ql.exec.vector.DoubleColumnVector;
import org.apache.hadoop.hive.ql.exec.vector.TimestampColumnVector;
import org.apache.hadoop.hive.ql.exec.vector.VectorizedRowBatch;
import org.apache.orc.CompressionKind;
import org.apache.orc.OrcFile;
import org.apache.orc.Reader;
import org.apache.orc.TypeDescription;
import org.apache.orc.Writer;

// Java program for downsampling an Apache ORC file containing only vectors of
// timestamps and floating-point values by a specific number of data points.
// It was implemented using the following resources for inspiration:
// - https://orc.apache.org/docs/core-java.html
// - https://orc.apache.org/api/orc-core/allclasses-noframe.html
// - https://github.com/skejserjensen/ModelarDB/blob/master/src/main/java/dk/aau/modelardb/core/timeseries/TimeSeriesORC.java
// - https://docs.oracle.com/en/java/javase/11/docs/api/java.sql/java/sql/Timestamp.html

class Main {
    public static void main(String args[]) throws IOException {
        if (args.length != 3) {
            usageAndExit();
        }

        var inputStringPath = args[0];
        var outputStringPath = args[1];
        var pointsToAggregate = Integer.valueOf(args[2]);

        if (pointsToAggregate == 1) {
            readAndWriteORCFile(inputStringPath, outputStringPath);
        } else if (pointsToAggregate > 1) {
            readAggregateAndWriteORCFile(inputStringPath, outputStringPath,
                pointsToAggregate);
        } else {
            usageAndExit();
        }
    }

    private static void usageAndExit() {
        System.out.println(
            "usage: java -jar uberjar input.orc output.orc points-to-aggregate");
        System.exit(0);
    }

    private static void readAndWriteORCFile(String inputStringPath,
        String outputStringPath) throws IOException {

        var reader = createORCReader(inputStringPath);
        var schema = reader.getSchema();
        var writer = createORCWriter(outputStringPath, schema);

        var recordReader = reader.rows();
        var recordBatch = schema.createRowBatch();

        while (recordReader.nextBatch(recordBatch)) {
            writer.addRowBatch(recordBatch);
        }

        writer.close();
        recordReader.close();
        reader.close();
    }


    private static void readAggregateAndWriteORCFile(String inputStringPath,
        String outputStringPath, int pointsToAggregate) throws IOException {

        var reader = createORCReader(inputStringPath);
        var schema = reader.getSchema();
        var writer = createORCWriter(outputStringPath, schema);

        var recordReader = reader.rows();
        var readerRecordBatch = schema.createRowBatch();
        var writerRecordBatch = schema.createRowBatch();

        // A timestamp and value is made for each column to simplify indexing.
        var pointsInWindow = 0;
        var timestampWindow = new Timestamp[readerRecordBatch.numCols];
        var valueWindow = new double[readerRecordBatch.numCols];

        while (recordReader.nextBatch(readerRecordBatch)) {
            for (int row = 0; row < readerRecordBatch.size; row++) {
                for (int column = 0; column < readerRecordBatch.numCols; column++) {
                    var vector = readerRecordBatch.cols[column];

                    // An exception is automatically raised on a wrong cast.
                    if (vector instanceof TimestampColumnVector) {
                        var timestampVector = (TimestampColumnVector) vector;
                        timestampWindow[column] = timestampVector.asScratchTimestamp(row);
                    } else {
                        var valueVector = (DoubleColumnVector) vector;
                        valueWindow[column] += valueVector.vector[row];
                    }
                }

                pointsInWindow++;

                if (pointsInWindow == pointsToAggregate) {
                    aggregateWindows(writerRecordBatch,
                        pointsInWindow,timestampWindow, valueWindow);
                    if (writerRecordBatch.size == writerRecordBatch.getMaxSize()) {
                        writer.addRowBatch(writerRecordBatch);
                        writerRecordBatch.reset();
                    }
                    pointsInWindow = 0;
                }
            }
        }

        aggregateWindows(writerRecordBatch,
            pointsInWindow,timestampWindow, valueWindow);
        if (writerRecordBatch.size != 0) {
            writer.addRowBatch(writerRecordBatch);
            writerRecordBatch.reset();
        }

        writer.close();
        recordReader.close();
        reader.close();
    }

    private static void aggregateWindows(VectorizedRowBatch writerRecordBatch,
        int pointsInWindow, Timestamp[] timestampWindow, double[] valueWindow) {

        int row = writerRecordBatch.size++;
        for (int column = 0; column < writerRecordBatch.numCols; column++) {
            var vector = writerRecordBatch.cols[column];

            // An exception is automatically raised on a wrong cast.
            if (vector instanceof TimestampColumnVector) {
                var timestampVector = (TimestampColumnVector) vector;
                timestampVector.set(row, timestampWindow[column]);
            } else {
                var valueVector = (DoubleColumnVector) vector;
                valueVector.vector[row] = valueWindow[column] / pointsInWindow;
                valueWindow[column] = 0.0f;
            }
        }
    }

    private static Reader createORCReader(String stringPath) throws IOException {
        var path = new Path(stringPath);
        var ro = OrcFile.readerOptions(new Configuration());
        return OrcFile.createReader(path, ro);
    }

    private static Writer createORCWriter(String stringPath,
        TypeDescription schema) throws IOException {

        var path = new Path(stringPath);
        var wo = OrcFile.writerOptions(new Configuration());

        // The schema is required to prevent a null-pointer exception due to:
        // https://github.com/apache/orc/blob/v1.6.14/java/core/src/java/org/apache/orc/impl/WriterImpl.java#L151
        wo.setSchema(schema);

        // The Python script used in experiments uses snappy instead of zlib.
        wo.compress(CompressionKind.SNAPPY);

        return OrcFile.createWriter(path, wo);
    }
}
