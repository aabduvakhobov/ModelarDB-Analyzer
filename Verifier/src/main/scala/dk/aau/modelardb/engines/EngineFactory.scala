/* Copyright 2018 The ModelarDB Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package dk.aau.modelardb.engines

import dk.aau.modelardb.core.{Configuration, Partitioner, SegmentGroup}
import dk.aau.modelardb.storage.Storage

import scala.collection.mutable
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions.{col, unix_timestamp}
import org.h2.table.TableFilter

object EngineFactory {

  /** Public Methods **/
  def startEngine(configuration: Configuration, storage: Storage): Unit = {
    verifier(configuration, storage)
  }

  private def verifier(configuration: Configuration, storage: Storage) = {


    if ( ! storage.isInstanceOf[dk.aau.modelardb.engines.spark.SparkStorage]) {
      throw new UnsupportedOperationException("CORE: verification is only supported for SparkStorage")
    }


    //Setup a Spark Session for connecting with the database
// TODO: case matching for storage type based on config file
    val sparkStorage = storage.asInstanceOf[dk.aau.modelardb.storage.ParquetStorage]

//    sparkStorage.rootFolder = "/home/abduvoris/ModelarDB-Home/ModelarDB-dev/ModelarDB/modelardb/"

    val engine = configuration.getString("modelardb.engine")


    //    val master = if (engine == "spark") "local[*]" else engine
    val master = "local[*]"
    val ssb = SparkSession.builder.master(master)

    val dimensions = configuration.getDimensions
    val spark = sparkStorage.open(ssb, dimensions)
    println("EVALUATION TOOL: -------------- MAX TID: " + sparkStorage.getMaxTid)

    sparkStorage.storeMetadataAndInitializeCaches(configuration, Array())

    var segmentGroupsDF = sparkStorage.getSegmentGroups(spark, Array()).orderBy("gid", "start_time")

    //-----------------------------------------
    val tidToGid = mutable.HashMap[Integer, Integer]()
    val timeSeriesMap = sparkStorage.getTimeSeries
    println("EVALUATION TOOL: Time Series HashMap: " + timeSeriesMap.size)

    for ((tid, metadata) <- timeSeriesMap) {
      val tsg = metadata(2).asInstanceOf[Int]
      tidToGid(tid) = tsg
      println(tid + " " + " GID: "+ tsg)
    }

    //---------------------------------------------
    val timeSeries = Partitioner.initializeTimeSeries(configuration, tidToGid.keys.min)
    println("EVALUATION TOOL: ------ SOURCE: ")
    timeSeries.foreach(x => println(x.source))

    println("Printing dims: ================================== "+ sparkStorage.dimensions)

//    var segmentGroupsDF = sparkStorage.getSegmentGroups(spark, Array()).orderBy("gid", "start_time")
    println("----------------------------------Now Show is diplayed--------------------------------------------------")
    segmentGroupsDF.printSchema()

    segmentGroupsDF = segmentGroupsDF
//      .withColumn("start_time_unix", unix_timestamp(col("start_time")))
      .withColumn("start_time", col("start_time").cast("long") * 1000)

    segmentGroupsDF = segmentGroupsDF
      .withColumn("end_time", unix_timestamp(col("end_time"))*1000)
//      .withColumn("end_time", (col("end_time")/1000).cast("long"))
    segmentGroupsDF.show(5)

    println(s"---------------Length of TS array: ${timeSeries.length}")

    println(s"----------------Length of TS iterator${timeSeries.iterator.length}")


    //Create variables for storing errors
    var differenceSum: Double = 0D
    var differenceTotal: Double = 0D
    var differenceCount = 0L
    var maxError = Float.MinValue

    val error = configuration.getErrorBound
//     filter sparkDF with tid over iteration
    for (timeSeries_id <- tidToGid.toSeq.sortBy(_._2)) {
      println(s"EVALUATION TOOL: CURRENT TID: --------------------- ${timeSeries_id._2}")
      val ts = timeSeries(timeSeries_id._2-1)
      ts.open()
      println("EVALUATION TOOL: CURRENT TID SOURCE: " + ts.source)
      val segmentGroup = segmentGroupsDF.filter(s"gid == ${timeSeries_id._2}")
      segmentGroup.show(5)
      val segmentItr = segmentGroup.rdd.toLocalIterator
      while (segmentItr.hasNext) {
        val row = segmentItr.next()
        val segmentGroup = new SegmentGroup(row(0).asInstanceOf[java.lang.Integer], row(1).asInstanceOf[java.lang.Long],
          row(2).asInstanceOf[java.lang.Long], row(3).asInstanceOf[java.lang.Integer],
          row(4).asInstanceOf[Array[Byte]], row(5).asInstanceOf[Array[Byte]])
        val segments = segmentGroup.toSegments(sparkStorage)
        for (segment <- segments) {
          val dataPoint = segment.grid().iterator()
          while (ts.hasNext & dataPoint.hasNext) {
            val r = ts.next()
            val a = dataPoint.next()

            if (timeSeries_id._2 == 8 & a.tid == 8) {
              println(s"REAL: ${r}")
              println(s"APPROXIMATE: ${a}")
            }

            val e = r.value - a.value
            val maxPercentageError = percentageError(r.value, a.value)
            if ((a.timestamp != r.timestamp) || (maxError > error)){
              throw new IllegalArgumentException(s"CORE: (A) ${a} and R $r with error $maxPercentageError cannot be verified")
            }

            maxError = Math.max(maxError, maxPercentageError)
            differenceCount += 1L
            differenceSum += Math.abs(r.value - a.value)
            differenceTotal += Math.abs(r.value)
          }
        }
      }

    }
    val message = new StringBuilder("EVALUATION RESULT:")
    message ++= s"\nMaximum real error bound $maxError"
    message ++= s"\nGeneral Count: $differenceCount"
    message ++= s"\nDifference Total: $differenceTotal"
    println(message)


    // you collect here everything and then map it to SegmentGroup class Array
    // and then array is iterated to get each particular segment out of it

  }

  private def percentageError(r: Float, a: Float) : Float = {
    val error = Math.abs((a - r) / r)
    error * 100
    val filter =

  }

}