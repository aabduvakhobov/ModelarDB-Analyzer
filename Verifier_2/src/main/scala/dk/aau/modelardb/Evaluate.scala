package dk.aau.modelardb

import dk.aau.modelardb.core.{Configuration, Partitioner, SegmentGroup, TimeSeriesGroup}
import dk.aau.modelardb.storage.Storage
import org.apache.spark.sql.SparkSession

import java.io.IOException
import java.util.logging.{FileHandler, Level, SimpleFormatter}
import scala.collection.mutable

object Evaluate {

  private var fh: FileHandler = _
  private var jobLogger: java.util.logging.Logger = _

  def verifier(configuration: Configuration, storage: Storage) = {
    val logger = getJobLogger
    //Setup a Spark Session for connecting with the database
    // TODO: case matching for storage type based on config file
    val configStorage = configuration.getStorage.split(":")(0).trim
    println(configStorage)
    val storageMedium =
      configStorage match {
        case "parquet" => storage.asInstanceOf[dk.aau.modelardb.storage.ParquetStorage]
        case "orc" => storage.asInstanceOf[dk.aau.modelardb.storage.ORCStorage]
        case "cassandra" => storage.asInstanceOf[dk.aau.modelardb.storage.CassandraStorage]
        case "jdbc" => storage.asInstanceOf[dk.aau.modelardb.storage.JDBCStorage]
        case _ => throw new UnsupportedOperationException("CORE: Storage medium is not supported")
      }
    //    val engine = configuration.getString("moderlardb.engine")
    //    sparkStorage.rootFolder = "/home/abduvoris/ModelarDB-Home/ModelarDB-dev/ModelarDB/modelardb/"

    val engine = configuration.getString("modelardb.engine")
    //    val master = if (engine == "spark") "local[*]" else engine
    storage.storeMetadataAndInitializeCaches(configuration, Array())
    //-------------------------------------------------
    //variables for storing errors
    val metrics = verifyError(storage, configuration) // pattern matching over here to choose engine type
    val message = new StringBuilder("EVALUATION RESULT:")
    // iterate over the map and print out as: TS: [metric1, metric2, ...]
    metrics.foreach(m => message ++= s"\n${m._1}: [${m._2}]")
    println(message)
    logger.info(message.toString())
  }

  private def getJobLogger = {
    if (jobLogger == null) {
      jobLogger = java.util.logging.Logger.getLogger("ResultLogs")
      try {
        fh = new FileHandler("./Verifier.log")
        fh.setFormatter(new SimpleFormatter)
        jobLogger.addHandler(fh)
      } catch {
        case e: SecurityException =>
          throw new RuntimeException(e)
        case e: IOException =>
          throw new RuntimeException(e)
      }
      jobLogger.setLevel(Level.INFO)
    }
    jobLogger
  }

  private def verifyError(storage: Storage, configuration: Configuration): mutable.Map[String, (BigInt, Double, Double, Double, Double, String)] = {
    if ( ! storage.isInstanceOf[dk.aau.modelardb.engines.spark.SparkStorage]) {
      throw new UnsupportedOperationException("CORE: verification is only supported for SparkStorage")
    }
    val sparkStorage = storage.asInstanceOf[dk.aau.modelardb.engines.spark.SparkStorage]
    //Detects the current data set used (EH / EP)
    val master = "local[*]"
    val ssb = SparkSession.builder.master(master).config("spark.driver.maxResultSize", "80g")

    val dimensions = configuration.getDimensions
    sparkStorage.storeMetadataAndInitializeCaches(configuration, Array())
//    val tidToGid = tidToGidMapper(storage)

    //---------------------------------------------
//    val timeSeries = Partitioner.initializeTimeSeries(configuration, tidToGid.keys.min-1)
    val timeSeries = Partitioner.initializeTimeSeries(configuration, 0)
    //    val dataSetPath = System.getProperty("user.home") + "/Data/" + dataSetName + "/"
    //val dataSetPath = "/user/cs.aau.dk/skj/home/Data/" + dataSetName + "/"
    val gsc = storage.getSourceGroupCache
    val error = configuration.getErrorBound
    val errors = Array.fill[Long](11)(0L)
    val nans = mutable.ArrayBuffer[String]()
    val mc = storage.getModelCache
    val modelsSegment = Array.fill[Long](mc.length)(0L)
    val modelsDataPoint = Array.fill[Long](mc.length)(0L)


    //Method for converting a Spark segment group row into a segment for the current sid
    import org.apache.spark.sql.Row

    val gmdc = storage.getGroupMetadataCache

    val rts = (row: Row, sid: Int) => {
      val model = mc(row.getInt(3))
      //Sampling interval
      val resolution = gmdc(row.getInt(0))(0)

      val exploded = new SegmentGroup(row.getInt(0), row.getTimestamp(1).getTime, row.getTimestamp(2).getTime,
        row.getInt(3), row.getAs[Array[Byte]](4), row.getAs[Array[Byte]](5)).explode(gmdc, storage.groupDerivedCache)

      exploded.filter(_.gid == sid).map(e => model.get(e.gid, e.startTime, e.endTime, resolution, e.model, e.offsets))
    }
    val spark = sparkStorage.open(ssb, dimensions)
    val maxSid = storage.getMaxTid
    //    val rows = sparkStorage.getSegmentGroups(spark, Array(org.apache.spark.sql.sources.EqualTo("gid", gsc(maxSid)))).collect()
    //    var generalCount: Long = 0
    val metricsMap = mutable.Map.empty[String, (BigInt, Double, Double, Double, Double, String)]
    //    Verify each data point
    var tid = 0
    while (tid < maxSid) {
      
      //Foreach sid verify that all data points are within the error bound and compute the average error
      var differenceSum: Double = 0.0
      var differenceTotal: Double = 0
      var differenceCount: Long = 0
      var generalCount: Long = 0
      var maxError = Double.MinValue
      var dataType: String = null
      // timeSeries array starts with 0 index, so it comes before tid+=1
      val ts = timeSeries(tid) // this might a problem a later on when grouping is implemented during ingestion
      ts.open()
      //get the correct ts file
      tid += 1
      val rows = sparkStorage.getSegmentGroups(spark, Array(org.apache.spark.sql.sources.EqualTo("gid", gsc(tid)))).orderBy( "start_time").collect()


      for (row <- rows) {
        val segment = rts(row, tid)
        //If a gap have occurred a segment group will not represent values for all time series in the group
        if (segment.nonEmpty) {
          //Update the number of models in segments
          modelsSegment(row.getInt(3)) += 1

          val it = segment(0).grid().iterator()
          while (it.hasNext && ts.hasNext) {
            //          while (it.hasNext) {
            val a = it.next()
            val r = ts.next()
            val e = dk.aau.modelardb.core.utility.Static.percentageError(a.value, r.value)

            if ((a.tid  != r.tid) || (a.timestamp != r.timestamp) || (e > error)) {
              throw new IllegalArgumentException(s"CORE: (A) $a and (R) $r with error $e cannot be verified")
            }
            //Update the number of models in data points
            modelsDataPoint(row.getInt(3)) += 1
            //            Update the, hopefully empty, list of NaN values
            if (a.value != r.value && Math.abs((r.value - a.value) / r.value).isNaN) {
              nans.append(r + "  " + a)
            }
            //            Update the ceilled errors histogram
            errors(Math.ceil(e).toInt) += 1L
            //            Updates the average error over the entire time series
            maxError = Math.max(maxError, e)
            if (e != 0.0) differenceCount += 1
            differenceSum += e
            differenceTotal += Math.abs(r.value)
            generalCount += 1
            if (generalCount == 1) dataType = f(r.value)
          }
        }
      }
      //      Verifies that the approximated time series contained enough data points
      if (ts.hasNext) {
        throw new IllegalArgumentException(s"CORE: $generalCount is less than the size of ${ts.source}")
      }

      val averageError = if (!(differenceSum/differenceCount).isNaN) differenceSum/differenceCount else 0D
      metricsMap(ts.source) = (generalCount, averageError, maxError, differenceCount, differenceSum, dataType)
    }
    metricsMap
  }


  private def tidToGidMapper(storage: Storage): mutable.HashMap[Integer, Integer] = {
    val tidToGid = mutable.HashMap[Integer, Integer]()
    val timeSeriesMap =  storage.getTimeSeries
    for ((tid, metadata) <- timeSeriesMap) {
      val tsg = metadata(2).asInstanceOf[Int]
      tidToGid(tid) = tsg
    }
    tidToGid
  }

  private def f[T](v:T) = v match {
    case _: Int => "Int"
    case _: Double => "Double"
    case _: Float => "Float"
    case _: Long => "Long"
    case _: Short => "Short"
    case _: BigInt => "BigInt"
    case _ => v.getClass.getName
  }

}