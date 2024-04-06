package com.stefanshome.simpletasks.ui.servers

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel

class ServersViewModel : ViewModel() {

    private val _text = MutableLiveData<String>().apply {
        value = "No servers configured"
    }
    val text: LiveData<String> = _text
}