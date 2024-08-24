package com.stefanshome.simpletasks

import android.util.Log
import com.stefanshome.simpletasks.ui.tasks.CollectionBody
import okhttp3.Call
import okhttp3.Callback
import okhttp3.Credentials
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okio.IOException
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import com.google.gson.JsonObject
import com.stefanshome.simpletasks.ui.tasks.TaskBody
import com.stefanshome.simpletasks.ui.tasks.TaskRecurrence

class ApiRequests {

    fun parseTasks(responseBody: String): CollectionBody {
        val gson = Gson()
        val type = object : TypeToken<CollectionBody>() {}.type
        val collectionBody: CollectionBody = gson.fromJson(responseBody, type)
        //Log.i("ParseTasks - Collection", "$collectionBody")
        return(collectionBody)
    }

    fun getCollection(callback: (CollectionBody?) -> Unit) {
        val credentials = Credentials.basic("", "")
        val client = OkHttpClient()

        val request = Request.Builder()
            .url("http://192.168.0.100:5000/tasks/my-grocery-list")
            .header("Authorization", credentials)
            .build()
        return client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
                Log.e("ApiRequests", "Failed to send GET request: ${e.message}")
                // Invoke the callback with null when request fails
                callback(null)
            }

            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                Log.i("ApiRequests", "Response Body - $responseBody")
                // Parse the response body to a Lit<TaskBody>
                //val collection = responseBody?.let { parseTasks(it) }
                val collection = responseBody?.let { parseTasks(it) }
                Log.i("ApiRequests", "Collection - $collection")
                // Invoke the callback with the response body
                callback(collection)
            }
        })
    }
}
