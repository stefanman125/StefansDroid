package com.stefanshome.simpletasks

import android.util.Log
import com.google.gson.Gson
import okhttp3.Call
import okhttp3.Callback
import okhttp3.Credentials
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okio.IOException

class ApiRequests {

    fun getTasks() {
        val credentials = Credentials.basic("", "passwd")
        val client = OkHttpClient()
        //val requestBody = jsonTask.toRequestBody("application/json".toMediaTypeOrNull())
        //Log.i("TESTING","Body $requestBody")

        //Log.i("TESTING", "Body Request $requestBody")

        val request = Request.Builder()
            .url("http://192.168.0.100:5000/tasks/my-grocery-list")
            .header("Authorization", credentials)
            .build()
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
                Log.e("TESTING", "Failed to send GET request: ${e.message}")
                // Handle failure
            }
            override fun onResponse(call: Call, response: Response) {
                val gson = Gson()
                val responseBody = response.body?.string()
                Log.i("TESTING", "$responseBody")
                //val taskResponse = gson.fromJson(responseBody, CollectionBody::class.java)
                // post data to live view _tasks.postValue(taskResponse.tasks)
                //Log.i("TESTING", "${taskResponse.tasks}")

            }
        })
    }
}