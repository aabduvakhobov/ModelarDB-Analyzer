/* Copyright 2022 The ModelarDB Contributors
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
package dk.aau.modelardb.integration

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.scala.DefaultScalaModule

import java.net.URI
import java.net.http.{HttpClient, HttpRequest, HttpResponse}

import scala.collection.SortedMap

class QueryTestHTTP extends QueryTest {

  override protected def getPorts: (Int, Int) = (9992, 9993)

  override protected def getInterface(port: Int): String = s"http:$port"

  override protected def executeQuery(query: String, port: Int): List[SortedMap[String, Object]] = {
    val client = HttpClient.newBuilder().build()
    val request = HttpRequest.newBuilder()
      .uri(URI.create("http://127.0.0.1:" + port))
      .POST(HttpRequest.BodyPublishers.ofString(query))
      .build()
    val response = client.send(request, HttpResponse.BodyHandlers.ofString())

    val mapper = new ObjectMapper
    mapper.registerModule(DefaultScalaModule)
    val result = mapper.readValue(response.body, classOf[Map[String, Object]])
    result("result").asInstanceOf[List[Map[String,Object]]].map(elem => SortedMap[String,Object]() ++ elem)
  }
}